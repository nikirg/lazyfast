from typing import Callable, ClassVar, Literal, Sequence

from dataclasses import dataclass
from fastapi import params

from lazyfast_old.dataclass import DataClass
from lazyfast_old.htmx import HTMX
from lazyfast_old import tags
from lazyfast_old import context
from lazyfast_old.state.base import StateField
from lazyfast_old.utils import url_join


SWAPPING_METHODS_MAP = {
    "replace": "innerHTML",
    "append": "beforeend",
    "prepend": "afterbegin",
}


@dataclass
class ComponentConfig:
    id: str | None = None
    path: str | None = None
    prefix: str | None = None
    dependencies: Sequence[params.Depends] | None = None
    reload_on: list[StateField] | None = None
    template_renderer: Callable | None = None
    preload_renderer: Callable | None = None
    class_: str | None = None
    swapping_method: Literal["replace", "append", "prepend"] = "replace"


class Component(DataClass):
    component_config: ClassVar[ComponentConfig]

    _container_id = None
    _url = None
    _class = None
    _id_prefix = "cid_"
    _loader_class = None
    _preload_renderer: Callable | None = None
    _loader_route_prefix = None
    _csrf_input_id = None

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
        
        if session.current_path:
            prefix = session.current_path.split(self._loader_route_prefix)[0]
        else:
            prefix = "/"

        url = url_join(prefix, self._url, query_params={"__cid__": component_id})
        htmx = HTMX(
            url=url,
            method="post",
            include=f"#{self._csrf_input_id}, #{container_id}",
            trigger=f"load, {container_id}",
        )

        with tags.div(
            class_=self._loader_class + " " + (self._class or ""),
            hx=htmx,
            id=container_id,
        ) as container:
            if self._preload_renderer:
                self._preload_renderer()

        self._container = container
