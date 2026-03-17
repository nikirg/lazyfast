import copy
import warnings
from typing import Self

from fastapi import Request

from lazyfast.dataclass import Serializable
from lazyfast.session import Session
from lazyfast.state.registry import StateField, StateFieldInterceptor

__all__ = ["State", "StateField"]


class State(Serializable, metaclass=StateFieldInterceptor):
    def __init__(self, request: Request):
        self._session: Session = request.state.session
        global_state_dict = self._session.state_data

        field_defaults: dict[str, object] = {}
        for cls in type(self).__mro__:
            field_defaults.update(getattr(cls, "__field_defaults__", {}))

        for field_name in self.fields:
            default_value = field_defaults.get(field_name)
            value = global_state_dict.get(field_name, default_value)
            setattr(self, field_name, copy.deepcopy(value))

    @classmethod
    async def load(cls, request: Request) -> "State":
        warnings.warn(
            "`load` method is deprecated, use `Depends(State)` instead",
            DeprecationWarning,
        )
        return cls(request)

    async def _reload_related_components(self) -> None:
        changed = self._get_changed_fields()
        # Traverse MRO so inheritance works: AppState.field triggers MyState's registry too
        for cls in type(self).__mro__:
            registry = cls.__dict__.get("__field_registry__", {})
            for field_name in changed:
                for component_id in registry.get(field_name, set()):
                    await self._session.put_updated_component_id(component_id)

    def _get_changed_fields(self) -> set[str]:
        fields: set[str] = set()
        global_state_data = self._session.state_data
        _sentinel = object()

        for field in self.fields:
            local_value = getattr(self, field)
            global_value = global_state_data.get(field, _sentinel)

            if global_value is _sentinel or local_value != global_value:
                fields.add(field)

        return fields

    def is_connection_alive(self) -> bool:
        if not hasattr(self, "_task_event"):
            self._task_event = self._session.new_task_slot()
        return not self._task_event.is_set()

    async def open(self) -> None:
        await self._session.state_lock.acquire()
        for field, value in self._session.state_data.items():
            setattr(self, field, copy.deepcopy(value))

    async def commit(self) -> None:
        # Always release the lock — even if reload triggers fail
        try:
            await self._reload_related_components()
            self._session.set_state_data(self.to_dict())
        finally:
            self._session.state_lock.release()

    async def __aenter__(self) -> Self:
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        # On exception: release lock but do NOT commit partial state
        if exc_type is not None:
            self._session.state_lock.release()
            return
        await self.commit()
