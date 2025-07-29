from collections import deque
from lazyfast.context.storage import ContextStorage


class TreeManager[T]:
    def __init__(self) -> None:
        self._storage = ContextStorage[deque[T]](
            "tree_nodes", default_factory=lambda: deque()
        )

    def get_all_nodes(self) -> list[T]:
        stack = self._storage.get() or deque()
        return list(stack)

    def append_node(self, node: T):
        if stack := self._storage.get():
            stack.append(node)
            self._storage.set(stack)

    def get_last_node(self) -> T | None:
        if stack := self._storage.get():
            return stack[-1]

    def update_last_node(self, node: T):
        if stack := self._storage.get():
            stack[-1] = node
            self._storage.set(stack)

    def pop_last_node(self):
        if stack := self._storage.get():
            stack.pop()
            self._storage.set(stack)

    def clear_stack(self):
        self._storage.reset()
