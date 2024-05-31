import inspect
import os
from typing import (
    Callable,
    ParamSpec,
    Sequence,
    Type,
    TypeVar,
)
from functools import wraps
from fastapi import Depends, APIRouter, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse

from renderable.htmx import HTMX
from renderable.component import Component
from renderable import context
from renderable.session import (
    SESSION_COOKIE_KEY,
    SESSION_COOKIE_MAX_AGE,
    Session,
    SessionStorage,
)
from renderable.state import State, StateField
from renderable import tags as tags

T = TypeVar("T", bound=Type[Component])

__all__ = ["RenderableRouter"]

LOADER_CLASS = "__componentLoader__"
LOADER_ROUTE = "/__renderable__/{}"

HTMX_CDN = "https://unpkg.com/htmx.org"
HTMX_SSE = f"{HTMX_CDN}/dist/ext/sse.js"

JS_SCRIPT = (
    """
function reloadComponent(element) {
    const componentLoader = element.closest('.%s');
    const cssSelector = '[data-htmx-indicator-class], [data-htmx-indicator-content]';
        
    const indicatorElmClass = element.closest('[data-htmx-indicator-class]');
    const indicatorElmContent = element.closest('[data-htmx-indicator-content]');
    
    if (indicatorElmClass) {
        if (indicatorElmClass.dataset.htmxIndicatorClass) {
            indicatorElmClass.classList.add(indicatorElmClass.dataset.htmxIndicatorClass);
        }
    }

    if (indicatorElmContent) {
        if (indicatorElmContent.dataset.htmxIndicatorContent) {
            indicatorElmContent.innerHTML = indicatorElmContent.dataset.htmxIndicatorContent;
        }
    }

    const tid = document.createElement("input");
    tid.type = "hidden";
    tid.name = "__tid__";
    tid.value = element.id;
    tid.style.display = 'none';
    tid.style.position = 'absolute';
    tid.style.zIndex = '-1';
    componentLoader.appendChild(tid)
    
    //componentLoader.dataset.htmxPost = componentLoader.dataset.htmxPost + '?tid=' + element.id;
    //componentLoader.dataset.htmxHeaders = `{'X-Trigger-Element-Id': ${element.id}}`;
    
    htmx.trigger(componentLoader, componentLoader.id);
}

htmx.on('htmx:sseError', function(evt){ document.location.reload(); });

function preventFormSubmission(event) {
    event.preventDefault();
}
"""
    % LOADER_CLASS
)


T = TypeVar("T")
P = ParamSpec("P")


class RenderableRouter(APIRouter):
    def __init__(
        self, state_schema: Type[State] | None = None, **fastapi_router_kwargs
    ):
        dependencies = fastapi_router_kwargs.get("dependencies", [])
        dependencies.append(Depends(self._get_or_create_session))
        fastapi_router_kwargs["dependencies"] = dependencies

        super().__init__(**fastapi_router_kwargs)

        self._state_schema = state_schema
        self._register_sse_endpoint()

    async def _init_state_schema(self) -> State | None:
        if self._state_schema:
            state = self._state_schema()
            try:
                await state.preload()
            except NotImplementedError:
                pass

            return state
        return None

    @staticmethod
    async def _load_inputs(request: Request):
        inputs = dict(await request.form())
        context.set_inputs(inputs)

    async def _get_or_create_session(
        self, request: Request, response: Response
    ) -> Session:
        session_id = request.cookies.get(SESSION_COOKIE_KEY)
        session = None

        if session_id:
            session = await SessionStorage.get_session(session_id)
            if not session:

                state = await self._init_state_schema()
                session = await SessionStorage.create_session(state)
        else:
            state = await self._init_state_schema()
            session = await SessionStorage.create_session(state)

        request.state.session = session
        context.set_session(session)

        if not session_id or session_id != session.id:
            response.set_cookie(
                key=SESSION_COOKIE_KEY,
                value=session.id,
                httponly=True,
                max_age=SESSION_COOKIE_MAX_AGE,
            )

        return session

    def _register_sse_endpoint(self):
        async def sse_endpoint(request: Request):
            async def event_stream():
                session: Session = request.state.session
                sid = session.id

                while True:
                    if await request.is_disconnected():
                        await SessionStorage.delete_session(sid)
                        break
                    component_id = await session.get_updated_component_id()
                    yield f"event: {component_id}\ndata: -\n\n"

            return StreamingResponse(event_stream(), media_type="text/event-stream")

        self.add_api_route(
            LOADER_ROUTE.format("sse"),
            sse_endpoint,
            response_class=StreamingResponse,
            include_in_schema=False,
        )

    @staticmethod
    def _replace_self(method: Callable) -> Callable:
        async def load_component_instance(id: str) -> Type[Component] | None:
            session = context.get_session()
            return session.get_component(id)

        sig = inspect.signature(method)

        if "self" not in sig.parameters:
            return method

        params = [param for name, param in sig.parameters.items() if name != "self"]
        self_dep_param = inspect.Parameter(
            "self",
            inspect.Parameter.KEYWORD_ONLY,
            default=Depends(load_component_instance),
        )
        params.append(self_dep_param)
        new_sig = sig.replace(parameters=params)

        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)

        wrapper.__signature__ = new_sig
        return wrapper

    def page(
        self,
        path: str,
        html_lang: str = "en",
        head: Callable | None = None,
        dependencies: Sequence[Depends] | None = None,
    ):
        def init_js_scripts():
            with tags.html(lang=html_lang):
                with tags.head():
                    tags.script(src=HTMX_CDN)
                    tags.script(src=HTMX_SSE)
                    tags.script(JS_SCRIPT)

                    if head:
                        head()

                hx = HTMX(ext="sse", sse_connect=LOADER_ROUTE.format("sse"))
                tags.body(hx=hx)

        def decorator(func: Callable) -> None:
            class PageComponent(Component):
                async def view(self):
                    pass

            setattr(PageComponent, "view", func)

            self.component(
                path=path, dependencies=dependencies, template=init_js_scripts
            )(PageComponent)

        return decorator

    def component(
        self,
        id: str | None = None,
        path: str | None = None,
        prefix: str = "/__renderable__",
        dependencies: Sequence[Depends] | None = None,
        reload_on: list[StateField] | None = None,
        template: Callable | None = None,
    ):
        deps = [Depends(self._load_inputs)]
        if dependencies:
            deps.extend(dependencies)

        def decorator(cls: Type[T]) -> Type[T]:
            if not isinstance(cls, type(Component)):
                raise TypeError("Decorated class must be a subclass of Component")

            view_func: Callable = getattr(cls, "view")
            is_async = inspect.iscoroutinefunction(view_func)
            view_func = self._replace_self(view_func)
            url = os.path.join(prefix, path or cls.__name__)

            if reload_on:
                if not id:
                    raise ValueError("id must be specified if reload_on is used")
                for state_field in reload_on:
                    state_field.register_component_reload(id)

            setattr(cls, "_container_id", id)
            setattr(cls, "_url", url)

            @wraps(view_func)
            async def endpoint(*args, **kwargs):
                context.clear_root_tags()

                if template:
                    template()

                try:
                    if is_async:
                        await view_func(*args, **kwargs)
                    else:
                        view_func(*args, **kwargs)

                    root_tags = context.get_root_tags()
                    html = "".join(tag.html() for tag in root_tags)
                    return html

                finally:
                    context.clear_root_tags()

            self.add_api_route(
                url,
                endpoint,
                dependencies=deps,
                response_class=HTMLResponse,
                methods=["GET", "POST"],
                include_in_schema=False,
            )

            return cls

        return decorator
