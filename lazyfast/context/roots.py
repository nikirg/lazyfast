from lazyfast.context.storage import ContextStorage


class RootNodesManager[T]:
    def __init__(self) -> None:
        self._storage = ContextStorage("root_nodes", default_factory=lambda: [])

    def get_root_nodes(self) -> list[T]:
        return self._storage.get() or []

    def clear_root_nodes(self) -> None:
        self._storage.reset()

    def add_root_node(self, node: T) -> None:
        if nodes := self._storage.get():
            nodes.append(node)
            self._storage.set(nodes)
        else:
            self._storage.set([node])
