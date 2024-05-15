import inspect
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
from renderable import context, tag as tags
from renderable.session import (
    SESSION_COOKIE_KEY,
    SESSION_COOKIE_MAX_AGE,
    Session,
    SessionStorage,
)
from renderable.state import State, StateField

__all__ = ["RenderableRouter"]

LOADER_CLASS = "__componentLoader__"
LOADER_ROUTE = "/__renderable__/{}"

HTMX_CDN = "https://unpkg.com/htmx.org"
HTMX_SSE = f"{HTMX_CDN}/dist/ext/sse.js"

JS_SCRIPT = (
    """
function reloadComponent(element) {
    const componentLoader = element.closest('.%s');
    componentLoader.setAttribute('hx-vals', JSON.stringify({ "__tid__": element.id }));
    componentLoader.querySelectorAll('[data-htmx-indicator-class]').forEach((el) => {
        el.classList.add(el.dataset['htmxIndicatorClass']);
    })
    componentLoader.querySelectorAll('[data-htmx-indicator-content]').forEach((el) => {
        el.innerHTML = el.dataset['htmxIndicatorContent'];
    })
    htmx.trigger(componentLoader, 'reload');

}
"""
    % LOADER_CLASS
)


T = TypeVar("T")
P = ParamSpec("P")


class Component:
    _tags: list[Type[tags.Tag]] = []

    def __init__(self) -> None:
        self._tags = []

    @property
    def inputs(self) -> dict[str, str]:
        return context.get_inputs()

    def add_tag(self, tag: Type[tags.Tag]):
        self._tags.append(tag)

    def html(self) -> str:
        return "".join([tag.html() for tag in self._tags])


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

    @staticmethod
    async def _load_inputs(request: Request):
        inputs = dict(await request.form())
        context.set_inputs(inputs)

    @staticmethod
    def _get_arg_names(func: Callable) -> list[str]:
        return [
            name
            for name, param in inspect.signature(func).parameters.items()
            if param.default == inspect.Parameter.empty
            and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
        ]

    async def _get_or_create_session(
        self, request: Request, response: Response
    ) -> Session:
        session_id = request.cookies.get(SESSION_COOKIE_KEY)
        session = None

        if session_id:
            session = await SessionStorage.get_session(session_id)
            if not session:
                state = self._state_schema()
                session = await SessionStorage.create_session(state)
        else:
            state = self._state_schema()
            session = await SessionStorage.create_session(state)

        request.state.session = session

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
                    yield f"event: {component_id}\ndata: <none>\n\n"

            return StreamingResponse(event_stream(), media_type="text/event-stream")

        self.add_api_route(
            LOADER_ROUTE.format("sse"),
            sse_endpoint,
            response_class=StreamingResponse,
            include_in_schema=False,
        )

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
                with tags.body(hx=hx):
                    pass

        def decorator(func: Callable) -> None:
            self.component(
                path=path, dependencies=dependencies, template=init_js_scripts
            )(func)

        return decorator

    def component(
        self,
        id: str | None = None,
        path: str | None = None,
        dependencies: Sequence[Depends] | None = None,
        reload_on: list[StateField] | None = None,
        template: Callable | None = None,
    ):
        if reload_on:
            if not id:
                raise ValueError("id is required when reload_on is set")

            for state_field in reload_on:
                state_field.register_component_reload(id)

        if dependencies:
            dependencies.append(Depends(self._load_inputs))
        else:
            dependencies = [Depends(self._load_inputs)]

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            @wraps(func)
            async def endpoint(*args, **kwargs) -> str:
                current_component = Component()
                context.set_component(current_component)

                if template:
                    template()

                try:
                    await func(*args, **kwargs)
                    return current_component.html()

                finally:
                    context.reset_component()

            route = path or LOADER_ROUTE.format(func.__name__)

            self.add_api_route(
                route,
                endpoint,
                dependencies=dependencies,
                response_class=HTMLResponse,
                methods=["POST", "GET"],
                include_in_schema=False,
            )

            positional_arg_names = self._get_arg_names(func)

            def wrapper(*args, **kwargs) -> None:
                path_params = {}
                query_params = dict(kwargs)
                url = route[:]

                for name, arg in zip(positional_arg_names, args):
                    if "{" + name + "}" in route:
                        path_params[name] = arg
                    else:
                        query_params[name] = arg

                url = (
                    url.format(**path_params)
                    + "?"
                    + "&".join(
                        [f"{key}={value}" for key, value in query_params.items()]
                    )
                )

                if url.endswith("?"):
                    url = url[:-1]

                trigger = "load, reload"
                if id:
                    trigger += f", sse:{id}"

                htmx = HTMX(
                    url=url,
                    method="post",
                    trigger=trigger,
                    include=f"closest .{LOADER_CLASS}",
                )

                tags.div(id=id, class_=LOADER_CLASS, hx=htmx)

            return wrapper

        return decorator
