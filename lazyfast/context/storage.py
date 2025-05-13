from typing import Callable
from asgiref.local import Local


class ContextStorage[T]:
    def __init__(
        self, attr_name: str, default_factory: Callable[[], T] | None = None
    ) -> None:
        self._attr_name = attr_name
        self._default_factory = default_factory
        self._local_data = Local()

        if default_factory:
            setattr(self._local_data, self._attr_name, default_factory)

    def get(self) -> T | None:
        return getattr(self._local_data, self._attr_name, None)

    def set(self, value: T) -> None:
        setattr(self._local_data, self._attr_name, value)

    def reset(self) -> None:
        if self._default_factory:
            setattr(self._local_data, self._attr_name, self._default_factory())
        else:
            if hasattr(self._local_data, self._attr_name):
                delattr(self._local_data, self._attr_name)
