import os, inspect, asyncio
from typing import (
    Callable,
    ParamSpec,
    Sequence,
    Type,
    TypeVar,
)
from functools import wraps

from fastapi import Depends, APIRouter, Request, Response, params
from fastapi.responses import HTMLResponse, StreamingResponse

from lazyfast import context, tags
from lazyfast.htmx import HTMX
from lazyfast.component import Component
from lazyfast.state import State, StateField
from lazyfast.session import ReloadRequest, Session, SessionStorage
from lazyfast.utils import url_join, extract_pattern


__all__ = ["LazyFastRouter"]


T = TypeVar("T")
P = ParamSpec("P")


with open(
    os.path.join(os.path.dirname(__file__), "script.js"), encoding="utf-8"
) as file:
    JS_SCRIPT_TEMPLATE = file.read()


class LazyFastRouter(APIRouter):
    def __init__(
        self,
        state_schema: Type[State] | None = None,
        session_cookie_key: str = "sid",
        session_cookie_max_age: int = 60 * 60 * 24 * 7,
        session_delete_timeout: int = 10,
        htmx_cdn: str = "https://unpkg.com/htmx.org",
        htmx_sse: str = "https://unpkg.com/htmx.org/dist/ext/sse.js",
        loader_class: str = "__componentLoader__",
        loader_route_prefix: str = "/__lazyfast__",
        sse_endpoint_dependencies: Sequence[params.Depends] | None = None,
        **fastapi_router_kwargs,
    ):
        """
        LazyFast Router

        This class provides routing functionalities for your web application, integrating state management, session handling, and HTMX support.

        Args:
            state_schema (Type[State], optional): Schema for managing the state. Defaults to None.
                Set this argument if you want to use the state manager and reload_on triggers.
            session_cookie_key (str, optional): Key for the session cookie. Defaults to "sid".
            session_cookie_max_age (int, optional): Maximum age of the session cookie in seconds. Defaults to one week (604800 seconds).
            session_delete_timeout (int, optional): Duration in seconds after a client disconnects, 
                beyond which the client's session is automatically terminated. Defaults to 10 seconds.
            htmx_cdn (str, optional): URL of the HTMX CDN. Defaults to "https://unpkg.com/htmx.org".
            htmx_sse (str, optional): URL of the HTMX SSE extension. Defaults to "https://unpkg.com/htmx.org/dist/ext/sse.js".
            loader_class (str, optional): CSS class for the component HTMX loader div. Defaults to "__componentLoader__".
            loader_route_prefix (str, optional): Prefix for the loader request route. Defaults to "/__lazyfast__".
            sse_endpoint_dependencies (Sequence[params.Depends], optional): Dependencies for the SSE endpoint. Defaults to None.

        Raises:
            TypeError: Raised if state_schema is not a subclass of State.

        Example:
            >>> router = LazyFastRouter(state_schema=State)
            >>> @router.page("/home")
            ... def home():
            ...     pass
        """
        self._loader_class = loader_class
        self._loader_route_prefix = loader_route_prefix
        self._htmx_cdn = htmx_cdn
        self._htmx_sse = htmx_sse
        self._session_cookie_key = session_cookie_key
        self._session_cookie_max_age = session_cookie_max_age
        self._session_delete_timeout = session_delete_timeout

        dependencies = fastapi_router_kwargs.get("dependencies", [])
        dependencies.append(Depends(self._load_session))
        dependencies.append(Depends(ReloadRequest))
        fastapi_router_kwargs["dependencies"] = dependencies

        self._js_script = JS_SCRIPT_TEMPLATE.replace(
            "__componentLoader__", loader_class
        )

        super().__init__(**fastapi_router_kwargs)

        self._state_schema = state_schema
        self._register_sse_endpoint(sse_endpoint_dependencies)

    async def _load_session(self, request: Request, response: Response) -> Session:
        session_id = request.cookies.get(self._session_cookie_key)
        state = self._state_schema() if self._state_schema else None
        session = None

        if session_id:
            session = await SessionStorage.get_session(session_id)
            if not session:
                session = await SessionStorage.create_session(state)
        else:
            session = await SessionStorage.create_session(state)

        session.set_current_path(extract_pattern(request.url.path, self.prefix))
        request.state.session = session
        context.set_session(session)

        if not session_id or session_id != session.id:
            response.set_cookie(
                key=self._session_cookie_key,
                value=session.id,
                httponly=True,
                max_age=self._session_cookie_max_age,
            )

        return session

    def _register_sse_endpoint(
        self, dependencies: Sequence[params.Depends] | None = None
    ):
        async def sse_endpoint(request: Request):
            session: Session = request.state.session
            sid = session.id

            async def event_stream():
                try:
                    while not (await request.is_disconnected()):
                        component_id = await session.get_updated_component_id()
                        yield f"event: {component_id}\ndata: -\n\n"
                finally:
                    await asyncio.sleep(self._session_delete_timeout)
                    if await request.is_disconnected():
                        await SessionStorage.delete_session(sid)

            return StreamingResponse(event_stream(), media_type="text/event-stream")

        self.add_api_route(
            url_join(self._loader_route_prefix, "sse"),
            sse_endpoint,
            response_class=StreamingResponse,
            include_in_schema=False,
            dependencies=dependencies,
        )

    @staticmethod
    def _replace_self(method: Callable) -> Callable:
        async def load_component_instance(__cid__: str) -> Type[Component] | None:
            session = context.get_session()
            component = session.get_component(__cid__)
            return component

        sig = inspect.signature(method)

        if "self" not in sig.parameters:
            return method

        args = [param for name, param in sig.parameters.items() if name != "self"]
        self_dep_param = inspect.Parameter(
            "self",
            inspect.Parameter.KEYWORD_ONLY,
            default=Depends(load_component_instance),
        )
        args.append(self_dep_param)
        new_sig = sig.replace(parameters=args)

        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)

        wrapper.__signature__ = new_sig
        return wrapper

    def page(
        self,
        path: str,
        html_lang: str = "en",
        head_renderer: Callable | None = None,
        dependencies: Sequence[Depends] | None = None,
    ):
        """Register a page

        Args:
            path (str): Fastapi path of the endpoint.
            html_lang (str, optional): Language value for "html" tag lang attribute. Defaults to "en".
            head_renderer (Callable | None, optional): A function that render html tags to head section.
                For example, it can be used to render meta, link, stryle or script tags
            dependencies (Sequence[Depends], optional): List of fastapi dependencies.

        Returns:
            Callable: A decorator that registers the page

        Raises:
            TypeError: If the path is not a string

        Example:
            >>> @app.page("/home")
            ... def home():
            ...     pass

        """

        def init_js_scripts(csrf_token: str | None = None):
            with tags.html(lang=html_lang):
                with tags.head():
                    tags.script(src=self._htmx_cdn)
                    tags.script(src=self._htmx_sse)
                    tags.script(self._js_script)

                    if head_renderer:
                        head_renderer()

                session = context.get_session()
                hx = HTMX(
                    ext="sse",
                    sse_connect=url_join(
                        session.current_path, self._loader_route_prefix, "sse"
                    ),
                )

                with tags.body(hx=hx):
                    tags.input(
                        id="csrf",
                        type_="hidden",
                        value=csrf_token,
                        name="csrf",
                        onchange=None,
                    )

        def decorator(func: Callable) -> None:
            class PageComponent(Component):
                async def view(self):
                    pass

            setattr(PageComponent, "view", func)
            
            self.component(
                path=path,
                dependencies=dependencies,
                template_renderer=init_js_scripts,
            )(PageComponent)

        return decorator

    def component(
        self,
        id: str | None = None,
        path: str | None = None,
        prefix: str | None = None,
        dependencies: Sequence[Depends] | None = None,
        reload_on: list[StateField] | None = None,
        template_renderer: Callable | None = None,
        preload_renderer: Callable | None = None,
        class_: str | None = None,
    ):
        """Register a component

        Args:
            id (str, optional): HTML id of the component div container.
                If not specified, a python object id will be used.
                If reload_on is used, id must be specified
            path (str, optional): Fastapi path of the component view endpoint
            prefix (str, optional): Path prefix of the component view endpoint
            dependencies (Sequence[Depends], optional): Fastapi dependencies of the component view endpoint
            reload_on (list[StateField], optional): State fields whose changes will cause the component to reload.
                Component id must be specified if reload_on is used. Works only if state_schema is set on router
            template_renderer (Callable | None, optional): A function that render html tags extra to the component div
            preload_renderer (Callable | None, optional): A function that preloads the component content. For example skeletons
            class_ (str | None, optional): The class of the component div

        Returns:
            Callable: A decorator that registers the component

        Raises:
            ValueError: If id is not specified and reload_on is used
            TypeError: If the class is not a subclass of Component

        Example:
            >>> @app.component()
            ... class MyComponent(Component):
            ...     async def view(self):
            ...         tags.p("Hello World")
        """

        def decorator(cls: Type[T]) -> Type[T]:
            if not isinstance(cls, type(Component)):
                raise TypeError("Decorated class must be a subclass of Component")

            view_func: Callable = getattr(cls, "view")

            if not callable(view_func):
                raise TypeError("Decorated class must have a view method")

            is_async = inspect.iscoroutinefunction(view_func)
            view_func = self._replace_self(view_func)
            url = url_join(
                prefix or ("/" if path != "/" else ""),
                path or url_join(self._loader_route_prefix, cls.__name__),
            )
   
            if reload_on:
                if not id:
                    raise ValueError("id must be specified if reload_on is used")
                if not self._state_schema:
                    raise ValueError(
                        "state_schema must be set on the router if reload_on is used"
                    )
                for state_field in reload_on:
                    state_field.register_component_reload(id)

            setattr(cls, "_container_id", id)
            setattr(cls, "_url", url)
            setattr(cls, "_class", class_)
            setattr(cls, "_loader_class", self._loader_class)
            setattr(cls, "_preload_renderer", preload_renderer)
            setattr(cls, "_loader_route_prefix", self._loader_route_prefix)

            @wraps(view_func)
            async def endpoint(*args, **kwargs):
                context.clear_root_tags()

                csrf_token = context.get_session().csrf_token

                if template_renderer:
                    template_renderer(csrf_token)

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
                dependencies=dependencies,
                response_class=HTMLResponse,
                methods=["GET", "POST"],
                include_in_schema=True,
            )

            return cls

        return decorator
