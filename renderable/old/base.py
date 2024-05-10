from abc import ABC
from typing import Type


class Renderable(ABC):
    _child_renderables: list[Type["Renderable"]] = []

    async def html(self) -> str:
        raise NotImplementedError

    # async def render(self) -> str:
    #     return "".join(
    #         [await renderable.html() for renderable in self._child_renderables]
    #     )

    @property
    def children(self) -> list[Type["Renderable"]]:
        return self._child_renderables

    def add_child(self, renderable: Type["Renderable"]):
        self._child_renderables.append(renderable)

    def clear_children(self):
        self._child_renderables = []
