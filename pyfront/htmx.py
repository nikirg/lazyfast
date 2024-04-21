from typing import Any, Literal, Type

from fastapi import FastAPI, Query, Request, Header
from fastapi.responses import HTMLResponse

from pyfront import context
from pyfront.component import Component
from pyfront.elements import div

METHOD_TYPE = Literal["get", "post", "put", "delete"]

SWAP_TYPE = Literal[
    "innerHTML",
    "outerHTML",
    "beforebegin",
    "afterbegin",
    "beforeend",
    "afterend",
    "delete",
    "none",
]

__all__ = ["HTMX"]


class Meta(type):
    def __getattribute__(cls, name):
        if name == "wrap":
            context.enable_htmx_wrapper()
        return super().__getattribute__(name)


class HTMX(metaclass=Meta):
    _components: dict[str, Type[Component]] = {}
    _htmx_endpoint_url: str | None = None

    def __init__(
        self,
        url: str | None = None,
        method: METHOD_TYPE = "get",
        trigger: str = "click",
        target: str | None = None,
        swap: SWAP_TYPE | None = None,
        select: str | None = None,
        vals: dict[str, Any] | str | None = None,
        include: str | None = None,
    ) -> None:
        if not self.__class__._htmx_endpoint_url:
            raise ValueError("HTMX.configure(app) must be called first")

        self._url = url
        self._method = method
        self._trigger = trigger
        self._target = target
        self._swap = swap
        self._select = select
        self._vals = vals
        self._include = include

        self._current_component = None
        self._current_parent_element = None

    @property
    def attrs(self) -> list[tuple[str, Any]]:
        return [
            (f"hx-{self._method}", self._url),
            ("hx-include", self._include),
            ("hx-trigger", self._trigger),
            ("hx-swap", self._swap),
            ("hx-select", self._select),
            ("hx-vals", self._vals),
            ("hx-target", self._target),
        ]

    @classmethod
    def configure(cls, app: FastAPI):
        cls._htmx_endpoint_url = "/_hx/{component_name}"

        @app.post(
            cls._htmx_endpoint_url, include_in_schema=True, response_class=HTMLResponse
        )
        async def _(
            request: Request,
            component_name: str,
        ):
            if "HX-Request" in request.headers:
                inputs = dict(await request.form())
                component = cls._components[component_name]
                html_str = await component.html(inputs)
                context.flush()
                return html_str

    @classmethod
    def wrap(cls, component: Type[Component]):
        try:
            if component.name not in cls._components:
                cls._components[component.name] = component

            url = cls._htmx_endpoint_url.format(component_name=component.name)

            htmx = cls(
                url=url,
                method="post",
                trigger="load, reload",
                include="closest .__componentLoader__",
            )
            div(class_="__componentLoader__", hx=htmx)
        finally:
            context.disable_htmx_wrapper()
