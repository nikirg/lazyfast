from functools import wraps
import inspect
from typing import (
    Callable,
    ParamSpec,
    Sequence,
    Type,
    TypeVar,
)
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse

from renderable.htmx import HTMX
from renderable import context, tag as tags

__all__ = ["RenderableApp"]

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


class RenderableApp(FastAPI):
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

        def decorator(func: Callable) -> None:
            self.component(
                path=path, dependencies=dependencies, template=init_js_scripts
            )(func)

        return decorator

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

    def component(
        self,
        id: str | None = None,
        path: str | None = None,
        dependencies: Sequence[Depends] | None = None,
        template: Callable | None = None,
    ):
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
                include_in_schema=True,
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

                htmx = HTMX(
                    url=url,
                    method="post",
                    trigger="load, reload",
                    include=f"closest .{LOADER_CLASS}",
                )

                tags.div(id=id, class_=LOADER_CLASS, hx=htmx)

            return wrapper

        return decorator
