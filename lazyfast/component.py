from typing import Any, Callable, ClassVar, Literal

from dataclasses import dataclass

from lazyfast.dataclass import DataClass
from lazyfast.htmx import HTMX
from lazyfast import tags
from lazyfast import context
from lazyfast.utils import url_join


_ID_PREFIX = "cid_"


@dataclass
class ComponentConfig:
    id: str | None = None
    class_: str | None = None
    swapping_method: Literal["replace", "append", "prepend"] = "replace"
    preload_renderer: Callable | None = None
    reload_on: list[Any] | None = None
    # Injected by router
    url: str = ""
    loader_class: str = "__componentLoader__"
    loader_route_prefix: str = "/__lazyfast__"
    csrf_input_id: str = "csrf"


class Component(DataClass):
    component_config: ClassVar[ComponentConfig]

    @property
    def component_id(self) -> str:
        return str(id(self))

    @property
    def container_id(self) -> str:
        return self.component_config.id or (_ID_PREFIX + self.component_id)

    async def view(self) -> None:
        raise NotImplementedError()

    async def reload(self) -> None:
        session = context.get_session()
        await session.put_updated_component_id(self.container_id)

    def __post_init__(self) -> None:
        cfg = self.component_config
        session = context.get_session()
        session.add_component(self)

        component_id = self.component_id
        container_id = self.container_id

        if session.current_path:
            prefix = session.current_path.split(cfg.loader_route_prefix)[0] or "/"
        else:
            prefix = "/"

        url = url_join(prefix, cfg.url, query_params={"__cid__": component_id})
        htmx = HTMX(
            url=url,
            method="post",
            include=f"#{cfg.csrf_input_id}, #{container_id}",
            trigger=f"load, {container_id}",
        )

        combined_class = (
            f"{cfg.loader_class} {cfg.class_}" if cfg.class_ else cfg.loader_class
        )

        with tags.div(class_=combined_class, hx=htmx, id=container_id) as container:
            if cfg.preload_renderer:
                cfg.preload_renderer()

        self._container = container
