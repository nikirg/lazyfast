from contextvars import ContextVar
from typing import Type

_components = ContextVar("components", default=[])
_elements = ContextVar("elements", default=[])
_is_htmx_wrapper = ContextVar("is_htmx_wrapper", default=False)


def set_component(component: Type["Component"]):
    components = _components.get()
    components.append(component)
    _components.set(components)


def get_component() -> Type["Component"] | None:
    components = _components.get()
    if components:
        return components[-1]
    
def reset_component():
    components = _components.get()
    if components:
        components.pop()
        _components.set(components)
        
def update_component(component: Type["Component"]):
    components = _components.get()
    if components:
        components[-1] = component
        _components.set(components)

def set_element(element: Type["HTMLElement"]):
    elements = _elements.get()
    elements.append(element)
    _elements.set(elements)
    
    
def get_element() -> Type["HTMLElement"] | None:
    elements = _elements.get()
    if elements:
        return elements[-1]
    
def reset_element():
    elements = _elements.get()
    if elements:
        elements.pop()
        _elements.set(elements)
        
def update_element(element: Type["HTMLElement"]):
    elements = _elements.get()
    if elements:
        elements[-1] = element
        _elements.set(elements)
    
def is_htmx_wrapper() -> bool:
    return _is_htmx_wrapper.get()


def enable_htmx_wrapper():
    _is_htmx_wrapper.set(True)
    
def disable_htmx_wrapper():
    _is_htmx_wrapper.set(False)
    
    
def flush():
    _components.set([])
    _elements.set([])
    _is_htmx_wrapper.set(False)