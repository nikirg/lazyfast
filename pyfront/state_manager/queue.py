import asyncio
from collections import defaultdict
from typing import Any


class StateQueue:
    def __init__(self):
        self.queues: dict[Any, asyncio.Queue] = defaultdict(asyncio.Queue)
        self.lock = asyncio.Lock()

    async def add(self, queue_id: Any):
        async with self.lock:
            if queue_id not in self.queues:
                self.queues[queue_id] = asyncio.Queue()

    async def delete(self, queue_id: Any):
        async with self.lock:
            if queue_id in self.queues:
                del self.queues[queue_id]

    async def enqueue(self, queue_id: Any, item: Any):
        async with self.lock:
            await self.queues[queue_id].put(item)

    async def dequeue(self, queue_id: Any) -> Any | None:
        async with self.lock:
            if self.queues[queue_id].empty():
                return None
            return await self.queues[queue_id].get()

    async def get_queue_size(self, queue_id: Any) -> int:
        async with self.lock:
            return self.queues[queue_id].qsize()


# # Пример использования
# async def main():
#     storage = AsyncQueueStorage()
#     await storage.add_queue('queue1')
#     await storage.enqueue('queue1', 'item1')
#     await storage.enqueue('queue1', 'item2')
#     print(await storage.dequeue('queue1'))  # Выведет: item1
#     print(await storage.get_queue_size('queue1'))  # Выведет: 1

# asyncio.run(main())
