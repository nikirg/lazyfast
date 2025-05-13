import inspect
from functools import lru_cache
from typing import Any, ClassVar, dataclass_transform


class Serializable:
    def __init__(self, **kwargs: Any):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))

    @property
    @lru_cache(maxsize=None)
    def fields(self) -> dict[str, Any]:
        parent_annotations = {
            field: type_
            for base in inspect.getmro(self.__class__)
            if hasattr(base, "__annotations__")
            for field, type_ in base.__annotations__.items()
            if getattr(type_, "__origin__", None) is not ClassVar
        }
        return parent_annotations | self.__class__.__annotations__

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        return {
            field: getattr(self, field)
            for field in self.fields
            if exclude is None or field not in exclude
        }


@dataclass_transform(kw_only_default=True)
class DataClass(Serializable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__post_init__()

    def __post_init__(self):
        pass
