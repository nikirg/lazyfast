from typing import dataclass_transform
from pydantic import BaseModel, Field

from renderable.htmx import HTMX
from renderable import tags
from renderable import context


class Component(BaseModel):
    _container_id = None
    _url = None

    async def view(self) -> None:
        raise NotImplementedError()

    def model_post_init(self, _):
        session = context.get_session()
        session.add_component(self)
        context.set_session(session)

        url = f"{self._url}?id={str(id(self))}"

        htmx = HTMX(
            url=url,
            method="post",
            include="#" + self._container_id,
            trigger=f"load, {self._container_id}, sse:{self._container_id}",
        )

        tags.div(class_="__componentLoader__", hx=htmx, id=self._container_id)
