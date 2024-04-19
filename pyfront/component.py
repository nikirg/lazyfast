from typing import Self, Type
from abc import ABC, abstractmethod

from pydantic import BaseModel

from pyfront.context import CURRENT_COMPONENT, CURRENT_PARENT_ELEMENT, IS_HTMX_WRAPPER


class Component(BaseModel, ABC):
    _elements: list[Type["HTMLElement"] | Type["Component"]] = []

    def __init__(self, **data):
        super().__init__(**data)
        self._register()

    def _register(self):
        if not IS_HTMX_WRAPPER.get():
            if elm := CURRENT_PARENT_ELEMENT.get():
                elm.add_child(self)
                CURRENT_PARENT_ELEMENT.set(elm)
            elif comp := CURRENT_COMPONENT.get():
                if comp != self:
                    comp.add_elm(self)
                    CURRENT_COMPONENT.set(comp)

    def __call__(self) -> Self:
        self._register()
        return self

    @property
    def name(self) -> str:
        return f"{self.__class__.__module__}.{self.__class__.__name__}"

    def add_elm(self, elm: Type["HTMLElement"] | Type["Component"]):
        self._elements.append(elm)

    def __getattribute__(self, name: str):
        if name == "view":
            CURRENT_COMPONENT.set(self)
            self._elements = []
        return super().__getattribute__(name)

    async def html(self, inputs: dict[str, str] | None = None) -> str:
        # TODO dependency injection
        self._inputs = inputs or {}
        await self.view()
        CURRENT_COMPONENT.set(None)
        html_repr = ""
        for elm in self._elements:
            html_repr += await elm.html()

        return html_repr

    @abstractmethod
    async def view(self) -> None:
        raise NotImplementedError

    def reload(self) -> str:
        pass
    
    def reloaded_by(self, elm: Type["HTTMElement"]) -> bool:
        return elm.id == self._inputs.get("__tid__")
            


class Root(Component):
    pass
