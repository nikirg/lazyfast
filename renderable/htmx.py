from typing import Any, Literal

__all__ = ["HTMX", "HTMX_PATH_TEMPLATE"]

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


HTMX_PATH_TEMPLATE = "/__htmx__/{component_id}"
HTMX_COMPONENT_LOADER_CLASS = "__componentLoader__"


class HTMX:
    def __init__(
        self,
        url: str | None = None,
        method: METHOD_TYPE | None = None,
        trigger: str | None = None,
        target: str | None = None,
        swap: SWAP_TYPE | None = None,
        select: str | None = None,
        vals: dict[str, Any] | str | None = None,
        include: str | None = None,
        ext: str | None = None,
        sse_connect: str | None = None,
    ) -> None:
        self._url = url
        self._method = method
        self._trigger = trigger
        self._target = target
        self._swap = swap
        self._select = select
        self._vals = vals
        self._include = include
        self._ext = ext
        self._sse_connect = sse_connect

        self._current_component = None
        self._current_parent_element = None

    @property
    def class_(self) -> str:
        return HTMX_COMPONENT_LOADER_CLASS

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
            ("hx-ext", self._ext),
            ("sse-connect", self._sse_connect),
        ]


def build_component_loader(component_name: str) -> HTMX:
    return HTMX(
        url=HTMX_PATH_TEMPLATE.format(component_id=component_name),
        method="post",
        trigger="load, reload",
        include=f"closest .{HTMX_COMPONENT_LOADER_CLASS}",
    )
