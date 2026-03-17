from typing import Any, dataclass_transform


class Serializable:
    def __init__(self, **kwargs: Any):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))

    @property
    def fields(self) -> dict[str, Any]:
        return type(self).__annotations__

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
