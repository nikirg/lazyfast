from contextvars import ContextVar
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class StackManager(Generic[T]):
    _contex_var: ContextVar

    def __init__(self, name: str) -> None:
        self._contex_var = ContextVar(name, default=[])
        
    @property
    def stack(self) -> list[T]:
        return self._contex_var.get()

    def append(self, elm: T):
        elms = self._contex_var.get()
        elms.append(elm)
        self._contex_var.set(elms)

    def get_last(self) -> T | None:
        if elms := self._contex_var.get():
            return elms[-1]

    def update_last(self, elm: T):
        if elms := self._contex_var.get():
            elms[-1] = elm
            self._contex_var.set(elms)

    def pop_last(self):
        if elms := self._contex_var.get():
            elms.pop()
            self._contex_var.set(elms)

    def clear(self):
        self._contex_var.set([])


_root_tags = ContextVar("root_tags", default=[])
_inputs = ContextVar("inputs", default={})
_session = ContextVar("session", default={})

def get_root_tags():
    return _root_tags.get()

def clear_root_tags():
    _root_tags.set([])
    
def add_root_tag(tag):
    _root_tags.get().append(tag)

# def set_component(component):
#     _current_component.set(component)


# def reset_component():
#     _current_component.set(None)


# def get_component():
#     return _current_component.get()


def set_inputs(inputs):
    _inputs.set(inputs)
    
def get_inputs():
    return _inputs.get()


def set_session(session: dict[str, Any]):
    _session.set(session)
    
def get_session() -> dict[str, Any]:
    return _session.get()