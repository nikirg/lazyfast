import warnings
from typing import Self

from fastapi import Request

from lazyfast_old.dataclass import Serializable
from lazyfast_old.session import Session
from lazyfast_old.state.registry import StateFieldInterceptor



class State(Serializable, metaclass=StateFieldInterceptor):
    def __init__(self, request: Request):
        self._session: Session = request.state.session
        global_state_dict = self._session.state_data

        for field_name in self.fields:
            default_value = getattr(self.__class__, field_name, None)
            value = global_state_dict.get(field_name, default_value)
            setattr(self, field_name, value)

    @staticmethod
    async def load(request: Request) -> "State":
        warnings.warn(
            "`load` method is deprecated, use `Depends(State)` instead",
            DeprecationWarning,
        )
        return State(request)

    async def _reload_related_components(self) -> None:
        for field_name in self._get_changed_fields():
            if component_ids := _field_to_component_ids.get(field_name):
                for component_id in component_ids:
                    await self._session.put_updated_component_id(component_id)

    def _get_changed_fields(self) -> set[str]:
        fields = set()
        global_state_data = self._session.state_data

        for field in self.fields:
            local_value = getattr(self, field)

            if global_value := global_state_data.get(field):
                if local_value != global_value:
                    fields.add(field)
            else:
                fields.add(field)

        return fields

    def _update_global_state_data(self) -> None:
        for field in self._get_changed_fields():
            self._session.state_data[field] = getattr(self, field)

    async def open(self) -> None:
        await self._session.state_lock.acquire()

    async def commit(self) -> None:
        self._session.set_state_data(self.to_dict())
        await self._reload_related_components()
        self._session.state_lock.release()

    async def __aenter__(self) -> Self:
        await self.open()
        return self

    async def __aexit__(self, *_) -> None:
        await self.commit()
