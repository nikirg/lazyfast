from collections import defaultdict


class StateFieldInterceptor(type):
    def __init__(cls, name: str, bases: tuple, namespace: dict) -> None:
        super().__init__(name, bases, namespace)
        field_defaults: dict[str, object] = {}
        for field_name in namespace.get("__annotations__", {}):
            if not field_name.startswith("_") and field_name in namespace:
                field_defaults[field_name] = namespace[field_name]
                delattr(cls, field_name)
        cls.__field_defaults__ = field_defaults
        # Each class definition gets its own fresh registry — no cross-class pollution
        cls.__field_registry__: dict[str, set[str]] = defaultdict(set)

    def __getattr__(cls, name: str) -> "StateField":
        # Find the class in MRO where the field is actually defined,
        # so StateField points to the right registry regardless of how it's accessed.
        for klass in cls.__mro__:
            annotations = klass.__dict__.get("__annotations__", {})
            if name in annotations and not name.startswith("_"):
                registry = klass.__dict__.get("__field_registry__", defaultdict(set))
                return StateField(name, registry)
        raise AttributeError(name)


class StateField:
    def __init__(self, name: str, registry: dict) -> None:
        self._name = name
        self._registry = registry

    def register_component_reload(self, component_id: str) -> None:
        self._registry[self._name].add(component_id)

    @property
    def name(self) -> str:
        return self._name
