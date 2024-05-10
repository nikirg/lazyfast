from abc import ABC
import asyncio
from typing import Any, Self, Type

from pydantic import BaseModel, model_validator


from renderable.base import Renderable
from renderable.context import component_stack, tag_stack, rendering_state, lazy_loading
from renderable.tag import div
from renderable.htmx import build_component_loader


class ComponentStorage:
    _id_to_component: dict[str, Type["Component"]] = {}
    _lock = asyncio.Lock()  # Создаем асинхронную блокировку

    @classmethod
    def add(cls, component_id: str, component: Type["Component"]):
        cls._id_to_component[component_id] = component

    @classmethod
    async def get(cls, component_id: str) -> Type["Component"] | None:
        async with cls._lock:  # Захват блокировки перед чтением данных
            return cls._id_to_component.get(component_id)


class Component(Renderable, BaseModel):
    id: str | None = None

    @model_validator(mode="before")
    @classmethod
    def set_values_from_session(cls, data: Any) -> Any:

        return data

    async def view(self):
        raise NotImplementedError

    async def html(self) -> str:
        self.clear_children()
        try:
            component_stack.append(self)
            await self.view()
            
        finally:
            component_stack.pop_last()

        return "".join([await renderable.html() for renderable in self.children])

    def _register(self):
        if parent_tag := tag_stack.get_last():
            parent_tag.add_child(self)
            tag_stack.update_last(parent_tag)

        elif parent_component := component_stack.get_last():
            parent_component.add_child(self)
            component_stack.update_last(parent_component)

        self._wrap_in_htmx()

    def _wrap_in_htmx(self):
        htmx = build_component_loader(self.__class__.__name__)
        div(class_=htmx.class_, hx=htmx)

    def __init__(self, **data):
        super().__init__(**data)

        if rendering_state.is_enabled():
            self._register()

    def __call__(self) -> Self:
        self._register()
        return self
