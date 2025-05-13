from collections import defaultdict

from pydantic._internal._model_construction import ModelMetaclass


class StateComponentRegistry:
    _field_to_component_ids: dict[str, set[str]] = defaultdict(set)


class StateFieldInterceptor(ModelMetaclass):
    def __getattr__(cls, name):
        if name := cls.__annotations__.get(name):
            if not name.startswith("_"):
                return StateField(name)
        return super().__getattr__(name)  # type: ignore


class StateField:
    _name: str

    def __init__(self, name: str):
        self._name = name

    def register_component_reload(self, component_id: str):
        _field_to_component_ids[self._name].add(component_id)

    @property
    def name(self) -> str:
        return self._name
