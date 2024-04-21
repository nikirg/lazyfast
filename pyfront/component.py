from typing import Any, Self, Type
from abc import ABC, abstractmethod
from pydantic import BaseModel
from pyfront import context


class Component(BaseModel, ABC):
    # A list to hold either HTMLElement or Component instances
    _elements: list[Type["HTMLElement"] | Type["Component"]] = []
    _inputs: dict[str, Any] = {}

    def __init__(self, **data):
        super().__init__(**data)
        self._register()  # Register component upon initialization

    def _register(self):
        # Register the component if not wrapped by HTMX
        if not context.is_htmx_wrapper():
            if elm := context.get_element():
                # If there's a parent element, add this component as a child
                elm.add_child(self)
                context.set_element(elm)
            elif comp := context.get_component():
                # If this component is not the current one, add it to the current component
                if comp != self:
                    comp.add_elm(self)
                    context.set_component(comp)

    def __call__(self) -> Self:
        # Make the component callable and re-register it each time it's called
        self._register()
        return self

    @property
    def name(self) -> str:
        # Generate a string representation of the component's class path
        return f"{self.__class__.__module__}.{self.__class__.__name__}"

    def add_elm(self, elm: Type["HTMLElement"] | Type["Component"]):
        # Add an element or another component to the _elements list
        self._elements.append(elm)

    def __getattribute__(self, name: str):
        # Custom attribute getter to handle 'view' specially
        if name == "view":
            # print(type(self))
            context.set_component(self)
            self._elements = []
        return super().__getattribute__(name)

    async def html(self, inputs: dict[str, str] | None = None) -> str:
        # Generate HTML representation of the component
        self._inputs = inputs or {}
        await self.view()  # Call the view to setup the component
        context.flush()
        html_repr = ""
        
        if self._elements:
            print(self.name)
        for elm in self._elements:
            html_repr += await elm.html()  # Append HTML from each element
        return html_repr

    @abstractmethod
    async def view(self) -> None:
        # Abstract method to be implemented by subclasses to define their view
        raise NotImplementedError

    def reload(self) -> str:
        # Method to handle component reloading (implementation needed)
        pass

    def reloaded_by(self, elm: Type["HTTMElement"]) -> bool:
        # Check if this component is reloaded by a specific HTMX element
        return elm.id == self._inputs.get("__tid__")
