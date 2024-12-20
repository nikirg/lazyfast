from pydantic import BaseModel

from lazyfast.htmx import HTMX
from lazyfast import tags
from lazyfast import context
from lazyfast.utils import url_join


SWAPPING_METHODS_MAP = {
    "replace": "innerHTML",
    "append": "beforeend",
    "prepend": "afterbegin",
}

class Component(BaseModel):
    _container_id = None
    _url = None
    _class = None
    _id_prefix = "cid_"
    _loader_class = None
    _preload_renderer = lambda: None
    _loader_route_prefix = None
    _csrf_input_id = None
    _swapping_method = "replace"

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

    def set_path_params(self, **kwargs):
        self._container.hx.set_path_params(**kwargs)

    def model_post_init(self, _):
        session = context.get_session()
        session.add_component(self)
        context.set_session(session)

        component_id = self.component_id
        container_id = self.container_id

        if prefix_path := session.prefix_path:
            prefix = prefix_path
        else:
            prefix = "/"

        url = url_join(prefix, self._url, query_params={"__cid__": component_id})
        htmx = HTMX(
            url=url,
            method="post",
            include=f"#{self._csrf_input_id}, #{container_id}",
            trigger=f"load, {container_id}",
            swap=f"{SWAPPING_METHODS_MAP[self._swapping_method]} transition:true",
        )

        with tags.div(
            class_=self._loader_class + " " + (self._class or ""),
            hx=htmx,
            id=container_id,
        ) as container:
            if self._preload_renderer:
                self._preload_renderer()

        self._container = container
