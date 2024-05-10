from typing import Any, Self, Type

from pydantic import BaseModel, Field

from pyfront import context
from pyfront.component import Component
from pyfront.htmx import HTMX


class State(BaseModel):
    _component_hash_to_state_fields = {}

    id: str

    @classmethod
    def link_field(cls, state_field_name: str | None = None) -> Any:
        print(type(state_field_name))
        print(context.get_component())

        print(cls._component_hash_to_state_fields)

        # cls._component_hash_to_state_fields[] = state_field_name

    def __init__(self, **data):
        data = context.get_session() | data
        super().__init__(**data)

    def _get_changed_fields(self, state_dict: dict[str, Any]) -> set[str]:
        session = context.get_session()
        session_fields = set(session.keys())
        state_fields = set(state_dict.keys())

        common_fields = session_fields.intersection(state_fields)

        changed_fields = {
            key for key in common_fields if session[key] != state_dict[key]
        }

        new_fields = state_fields - session_fields
        return changed_fields | new_fields

    async def _reload_related_components(self, fields: set[str]) -> None:
        for field_name in fields:
            # HTMX.reload(component)
            pass

    async def commit(self) -> None:
        state_dict = self.model_dump(exclude_unset=True)
        changed_fields = self._get_changed_fields(state_dict)
        await self._reload_related_components(changed_fields)
        context.set_session(state_dict)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_) -> None:
        await self.commit()
