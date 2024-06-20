from pydantic import BaseModel

from renderable.htmx import HTMX
from renderable import tags
from renderable import context


class Component(BaseModel):
    _container_id = None
    _url = None
    _class = None
    _id_prefix = "cid_"

    @property
    def component_id(self) -> str:
        return str(id(self))

    @property
    def container_id(self) -> str:
        return self._container_id or (self._id_prefix + self.component_id)

    async def view(self) -> None:
        raise NotImplementedError()

    async def reload(self):
        session = context.get_session()
        await session.state.enqueue(self.container_id)

    def model_post_init(self, _):
        session = context.get_session()
        session.add_component(self)
        context.set_session(session)

        component_id = self.component_id
        container_id = self.container_id

        url = f"{self._url}?id={component_id}"

        htmx = HTMX(
            url=url,
            method="post",
            include="#" + container_id,
            trigger=f"load, {container_id}, sse:{container_id}",
        )

        tags.div(
            class_="__componentLoader__" + (self._class or ""),
            hx=htmx,
            id=container_id,
        )
