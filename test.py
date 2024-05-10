from typing import dataclass_transform
from pydantic import BaseModel, Field
from pydantic._internal._model_construction import ModelMetaclass

@dataclass_transform(kw_only_default=True, field_specifiers=(Field,))
class ModelMeta(ModelMetaclass):
    def __getattr__(cls, name):
        if name in cls.__annotations__:
            return name
        return super().__getattr__(name)

class State(BaseModel, metaclass=ModelMeta):
    group: str = "internal"
    
    def load(self):
        pass

# Тестирование
print(State.group)  # Доступ к значению через класс, будет запущена логика класса
state = State()
print(state.group)  # Доступ к значению через экземпляр, будет возвращено стандартное значение
state.group = "external"  # Установка значения через экземпляр
print(state.group)  # Доступ к установленному значению через экземпляр


State()