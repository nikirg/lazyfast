import hashlib
from typing import Any, Generic, Self, Type, TypeVar
from abc import ABC, abstractmethod

from fastapi import Request
from pydantic import BaseModel
from pyfront import context
from pyfront.elements import div
from pyfront.htmx import HTMX

# from pyfront.state import State


T = TypeVar("T", bound=BaseModel)

class ComponentStorage:
    _components: dict[str, Type[Self]] = {}
    
    @classmethod
    def add(cls, component_id: str, component: Type[Self]):
        cls._components[component_id] = component
    
    @classmethod
    def get(cls, component_id: str) -> Type[Self] | None:
        return cls._components.get(component_id)
    
    


class Component(BaseModel, ABC):
    id: str | None = None
    # A list to hold either HTMLElement or Component instances

    _elements: list[Type["HTMLElement"] | Type["Component"]] = []
    _inputs: dict[str, Any] = {}
    
    
    @abstractmethod
    async def view(self) -> None:
        # Abstract method to be implemented by subclasses to define their view
        raise NotImplementedError

    def __init__(self, **data):
        super().__init__(**data)
        self._register()  # Register component upon initialization

    def __call__(self) -> Self:
        # Make the component callable and re-register it each time it's called
        self._register()
        return self

    def __hash__(self) -> int:
        data = (
            self.__class__.__module__
            + self.__class__.__name__
            + self.model_dump_json(exclude_none=True)
        )
        data_bytes = data.encode()
        hash_object = hashlib.sha256()
        hash_object.update(data_bytes)
        return int(hash_object.hexdigest(), 16)


    def __getattribute__(self, name: str):
        # Custom attribute getter to handle 'view' specially
        if name == "view":
            context.set_component(self)
            self._elements = []
        return super().__getattribute__(name)
    
    def _wrap_in_htmx(self):
        component_id = self.id or str(hash(self))
        
        component = ComponentStorage.get(component_id)
            
        if not component:
            ComponentStorage.add(component_id, self)

        url = HTMX.endpoint_url.format(component_id=component_id)
        elm_id = f"cid_{component_id}"

        htmx = HTMX(
            url=url,
            method="post",
            trigger=f"load, reload, sse:{elm_id}",
            include="closest .__componentLoader__",
        )
        div(id=elm_id, class_="__componentLoader__", hx=htmx)
    
    def _register(self):
    # Register the component if not wrapped by HTMX    
        if context.is_htmx_wrapper_disabled():
            if elm := context.get_element():
                # If there's a parent element, add this component as a child
                elm.add_child(self)

            elif comp := context.get_component():
                # If this component is not the current one, add it to the current component
                if comp != self:
                    comp.add_elm(self)
                    
        else:
            self._wrap_in_htmx()
                        
                    
    def add_elm(self, elm: Type["HTMLElement"] | Type["Component"]):
        # Add an element or another component to the _elements list
        self._elements.append(elm)

    async def html(
        self, request: Request | None = None, inputs: dict[str, str] | None = None
    ) -> str:
        # Generate HTML representation of the component
        self._inputs = inputs or {}

        # if request:
        #     context.set_session(request.session)

        try:
            await self.view()  # Call the view to setup the component
        finally:
            # if request:
            #     request.session.clear()
            #     request.session.update(context.get_session())
            context.flush()

        html_repr = "".join([await elm.html(request) for elm in self._elements])
        return html_repr

    def reload(self) -> str:
        # Method to handle component reloading (implementation needed)
        pass

    def reloaded_by(self, elm: Type["HTTMElement"]) -> bool:
        # Check if this component is reloaded by a specific HTMX element
        return elm.id == self._inputs.get("__tid__")
