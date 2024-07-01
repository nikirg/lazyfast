import json
from typing import Any, Literal

__all__ = ["HTMX"]

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
        sse_swap: str | None = None,
        headers: dict[str, str] | None = None,
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
        self._headers = headers
        self._sse_connect = sse_connect
        self._sse_swap = sse_swap

        self._current_component = None
        self._current_parent_element = None

    def set_path_params(self, **kwargs):
        self._url = self._url.format(**kwargs)

    @property
    def attrs(self) -> list[tuple[str, Any]]:
        return [
            (f"hx-{self._method}", self._url),
            ("hx-include", self._include),
            ("hx-trigger", self._trigger),
            ("hx-swap", self._swap),
            ("hx-select", self._select),
            (
                "hx-vals",
                json.dumps(self._vals) if isinstance(self._vals, dict) else self._vals,
            ),
            ("hx-target", self._target),
            ("hx-ext", self._ext),
            ("hx-headers", json.dumps(self._headers) if self._headers else None),
            ("sse-connect", self._sse_connect),
            ("sse-swap", self._sse_swap),
            ("hx-encoding", "multipart/form-data"),
        ]
