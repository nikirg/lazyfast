from collections import deque
import asyncio, uuid
from typing import Generator, Type

from lazyfast.cache import Cache
from lazyfast.component import Component
from lazyfast.request import ReloadRequest
from lazyfast.state import State
from lazyfast.utils import generate_csrf_token


class Session:
    def __init__(
        self, session_id: str, state: State | None = None, buffer_size: int = 10
    ) -> None:
        self._session_id = session_id
        self._queue = asyncio.Queue()
        self._components: dict[int, Type["Component"]] = {}
        self._csrf_token = generate_csrf_token()
        self._current_path = None
        self._reload_request = None
        self._buffer = deque(maxlen=buffer_size)
        self._cache = Cache()

        if state:
            state.set_queue(self._queue)

        self._state = state

    @property
    def csrf_token(self) -> str | None:
        return self._csrf_token

    @property
    def id(self) -> str:
        return self._session_id

    @property
    def state(self) -> State:
        return self._state

    @property
    def reload_request(self) -> ReloadRequest:
        return self._reload_request

    @property
    def current_path(self) -> str | None:
        return self._current_path
    
    @property
    def cache(self) -> Cache:
        return self._cache

    def set_reload_request(self, request: ReloadRequest) -> None:
        self._reload_request = request

    def set_current_path(self, path: str) -> None:
        self._current_path = path

    def set_state(self, state: State) -> None:
        self._state = state

    async def get_updated_component_id(self) -> str | None:
        if not self._state:
            return

        component_id = await self._state.dequeue()
        self._buffer.append(component_id)
        return component_id

    def get_missed_events(self, last_event: str) -> Generator[None, None, str]:
        idx = self._buffer.index(last_event) if last_event in self._buffer else -1
        if idx != -1:
            for i, item in enumerate(self._buffer):
                if i > idx:
                    yield item

    def add_component(self, component: Type["Component"]) -> None:
        self._components[str(id(component))] = component

    def get_component(self, component_id: str) -> Type["Component"]:
        return self._components[str(component_id)]


class SessionStorage:
    _sessions: dict[str, Session] = {}
    _lock: asyncio.Lock = asyncio.Lock()

    @classmethod
    async def get_session(cls, session_id: str) -> Session | None:
        return cls._sessions.get(session_id)

    @classmethod
    async def create_session(
        cls, state: Type[State] | None = None, buffer_size: int = 10
    ) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(session_id, state, buffer_size=buffer_size)

        async with cls._lock:
            cls._sessions[session_id] = session

        return session

    @classmethod
    async def update_session(cls, session_id: str, data: dict) -> None:
        session = await cls.get_session(session_id)
        if session:
            async with cls._lock:
                session.set_data(data)

    @classmethod
    async def delete_session(cls, session_id: str) -> None:
        if session_id in cls._sessions:
            async with cls._lock:
                del cls._sessions[session_id]
