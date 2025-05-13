import uuid
import asyncio
from collections import deque
from typing import Any, ClassVar, Generator, Type

from lazyfast_old.cache import Cache
from lazyfast_old.component import Component
from lazyfast_old.request import ReloadRequest
from lazyfast_old.utils import generate_csrf_token


class Session:
    def __init__(self, session_id: str, buffer_size: int = 10) -> None:
        self._session_id = session_id
        self._queue = asyncio.Queue[str]()
        self._components: dict[str, Component] = {}
        self._csrf_token = generate_csrf_token()
        self._current_path = None
        self._reload_request = None
        self._buffer = deque[str](maxlen=buffer_size)
        self._state_data: dict[str, Any] = {}
        # self._cache = Cache()
        self._state_lock = asyncio.Lock()

    @property
    def csrf_token(self) -> str | None:
        return self._csrf_token

    @property
    def id(self) -> str:
        return self._session_id

    @property
    def state_data(self) -> dict[str, str]:
        return dict(self._state_data)
    
    def set_state_data(self, state_data: dict[str, str]):
        self._state_data = state_data

    # @property
    # def state(self) -> State:
    #     return self._state

    # @property
    # def cache(self) -> Cache:
    #     return self._cache

    # def set_state(self, state: State) -> None:
    #     self._state = state
    @property
    def reload_request(self) -> ReloadRequest | None:
        return self._reload_request

    @property
    def current_path(self) -> str | None:
        return self._current_path

    def set_reload_request(self, request: ReloadRequest) -> None:
        self._reload_request = request

    def set_current_path(self, path: str) -> None:
        self._current_path = path

    async def put_updated_component_id(self, component_id: str) -> None:
        await self._queue.put(component_id)

    async def get_updated_component_id(self) -> str | None:
        component_id = await self._queue.get()
        self._buffer.append(component_id)
        return component_id

    def get_missed_events(self, last_event: str) -> Generator[str, None, None]:
        idx = self._buffer.index(last_event) if last_event in self._buffer else -1
        if idx != -1:
            for i, item in enumerate(self._buffer):
                if i > idx:
                    yield item

    def add_component(self, component: Type["Component"]) -> None:
        self._components[str(id(component))] = component

    def get_component(self, component_id: str) -> Type["Component"]:
        return self._components[str(component_id)]

    @property
    def state_lock(self) -> asyncio.Lock:
        return self._state_lock


class SessionStorage:
    _sessions: ClassVar[dict[str, Session]] = {}
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    @classmethod
    async def get_session(cls, session_id: str) -> Session | None:
        return cls._sessions.get(session_id)

    @classmethod
    async def create_session(cls, buffer_size: int = 10) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(session_id, buffer_size=buffer_size)

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
