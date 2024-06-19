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
    
    async def reload(self):
        session = context.get_session()
        await session.state.enqueue(id(self))
        
    def model_post_init(self, _):
        session = context.get_session()
        session.add_component(self)
        context.set_session(session)

        container_id = self._container_id or str(id(self))

        prefix = "cid_"
        url = f"{self._url}?id={container_id}"

        htmx = HTMX(
            url=url,
            method="post",
            include="#" + prefix + container_id,
            trigger=f"load, {prefix}{container_id}, sse:{container_id}",
            #vals='js:{__tid__: event?.detail?.__tid__}',
        )

        tags.div(class_="__componentLoader__", hx=htmx, id=prefix + container_id)
