import warnings
from typing import Generic, TypeVar
from fastapi import Depends, HTTPException, Request

T = TypeVar("T")


async def _load_form_data(request: Request) -> dict[str, str]:
    return dict(await request.form())


class ReloadRequest(Generic[T]):
    def __init__(
        self, request: Request, inputs: dict[str, str] = Depends(_load_form_data)
    ) -> None:
        self._method = request.method
        self._session_id = request.state.session.id

        if self._method != "GET":
            csrf_token = inputs.get("csrf")

            if csrf_token != request.state.session.csrf_token:
                raise HTTPException(status_code=403, detail="Invalid CSRF token")

        self._trigger_id = inputs.get("__tid__")
        self._trigger_event = inputs.get("__evt__")

        if self._trigger_id:
            del inputs["__tid__"]
        if self._trigger_event:
            del inputs["__evt__"]
        self._inputs = inputs

        request.state.session.set_reload_request(self)

    @property
    def method(self) -> str:
        return self._method

    @property
    def trigger_id(self) -> str | None:
        return self._trigger_id

    @property
    def trigger_event(self) -> str | None:
        return self._trigger_event

    @property
    def data(self) -> dict[str, str] | None:
        warnings.warn(
            "`data` property is deprecated, use `inputs` instead", DeprecationWarning
        )
        return dict(self._inputs)

    @property
    def inputs(self) -> T | None:
        return self._inputs

    @property
    def session_id(self) -> str:
        return self._session_id
