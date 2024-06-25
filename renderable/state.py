import asyncio
from collections import defaultdict
from typing import Any, Self, dataclass_transform
from fastapi import Request
from pydantic import BaseModel, Field
from pydantic._internal._model_construction import ModelMetaclass

field_to_components: dict[str, list[str]] = defaultdict(set)


class StateField:
    _name: str

    def __init__(self, name: str):
        self._name = name

    def register_component_reload(self, component_id: str):
        field_to_components[self._name].add(component_id)

    @property
    def name(self) -> str:
        return self._name


@dataclass_transform(kw_only_default=True, field_specifiers=(Field,))
class ModelMeta(ModelMetaclass):
    def __getattr__(cls, name):
        if name in cls.__annotations__ and not name.startswith("_"):
            return StateField(name)
        return super().__getattr__(name)


class State(BaseModel, metaclass=ModelMeta):
    _queue: asyncio.Queue | None = None
    _dump: dict[str, Any] = {}

    @staticmethod
    async def load(request: Request) -> Self:
        return request.state.session.state

    def set_queue(self, queue: asyncio.Queue):
        self._queue = queue

    def dequeue(self) -> Any:
        return self._queue.get()

    async def enqueue(self, value: Any) -> None:
        await self._queue.put(value)

    @staticmethod
    def _compare_dicts(data1: dict[str, Any], data2: dict[str, Any]) -> set[str]:
        changed_fields = set()
        all_keys = set(data1.keys()).union(set(data2.keys()))

        for key in all_keys:
            if key not in data1 or key not in data2:
                changed_fields.add(key)
            elif data1[key] != data2[key]:
                changed_fields.add(key)

        return changed_fields

    async def _reload_related_components(self, fields: set[str]) -> None:
        for field_name in fields:
            if components := field_to_components.get(field_name):
                for component_id in components:
                    await self.enqueue(component_id)

    def open(self) -> None:
        self._dump = self.model_dump()

    async def commit(self) -> None:
        changed_fields = self._compare_dicts(self._dump, self.model_dump())
        await self._reload_related_components(changed_fields)

    async def __aenter__(self) -> Self:
        self.open()
        return self

    async def __aexit__(self, *_) -> None:
        await self.commit()
