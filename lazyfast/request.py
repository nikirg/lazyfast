from typing import cast
import warnings

from starlette.datastructures import UploadFile
from fastapi import Depends, HTTPException, Request

FormData = dict[str, UploadFile | str]


async def _load_form_data(request: Request) -> FormData:
    return dict(await request.form())


class ReloadRequest:
    def __init__(
        self,
        request: Request,
        inputs: FormData = Depends(_load_form_data),
    ) -> None:
        self._method = request.method
        self._session_id = request.state.session.id

        if self._method != "GET":
            csrf_token = inputs.get("csrf")

            if csrf_token != request.state.session.csrf_token:
                raise HTTPException(status_code=403, detail="Invalid CSRF token")

        self._trigger_id = cast(str | None, inputs.get("__tid__"))
        self._trigger_event = cast(str | None, inputs.get("__evt__"))
        self._inputs: FormData = {
            k: v for k, v in inputs.items() if k not in ("__tid__", "__evt__", "csrf")
        }

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
    def data(self) -> FormData:
        warnings.warn(
            "`data` property is deprecated, use `inputs` instead", DeprecationWarning
        )
        return dict(self._inputs)

    @property
    def inputs(self) -> FormData:
        return self._inputs

    @property
    def session_id(self) -> str:
        return self._session_id
