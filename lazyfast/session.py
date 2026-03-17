import time
import uuid
import asyncio
from collections import deque
from typing import TYPE_CHECKING, Any, ClassVar, Generator

from lazyfast.request import ReloadRequest
from lazyfast.utils import generate_csrf_token

if TYPE_CHECKING:
    from lazyfast.component import Component


class _TTLDict:
    """Dict that auto-expires entries after `ttl` seconds. No external deps."""

    def __init__(self, ttl: float) -> None:
        self._data: dict[str, Any] = {}
        self._ts: dict[str, float] = {}
        self._ttl = ttl

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._ts[key] = time.monotonic()

    def __getitem__(self, key: str) -> Any:
        if key not in self._data:
            raise KeyError(key)
        if time.monotonic() - self._ts[key] > self._ttl:
            del self._data[key]
            del self._ts[key]
            raise KeyError(key)
        return self._data[key]

    def __contains__(self, key: object) -> bool:
        try:
            self[str(key)]
            return True
        except KeyError:
            return False

    def evict_expired(self) -> None:
        now = time.monotonic()
        expired = [k for k, t in self._ts.items() if now - t > self._ttl]
        for k in expired:
            del self._data[k]
            del self._ts[k]


class Session:
    def __init__(
        self, session_id: str, buffer_size: int = 10, component_ttl: float = 300
    ) -> None:
        self._session_id = session_id
        self._queue = asyncio.Queue[str]()
        self._pending_component_ids: set[str] = set()  # dedup tracker
        self._components: _TTLDict = _TTLDict(ttl=component_ttl)
        self._csrf_token = generate_csrf_token()
        self._current_path = None
        self._reload_request = None
        self._buffer = deque[str](maxlen=buffer_size)
        self._state_data: dict[str, Any] = {}
        self._state_lock = asyncio.Lock()
        self._current_task_event: asyncio.Event | None = None

    @property
    def csrf_token(self) -> str | None:
        return self._csrf_token

    @property
    def id(self) -> str:
        return self._session_id

    @property
    def state_data(self) -> dict[str, Any]:
        return dict(self._state_data)

    def set_state_data(self, state_data: dict[str, Any]) -> None:
        self._state_data = state_data

    @property
    def reload_request(self) -> ReloadRequest | None:
        return self._reload_request

    @property
    def current_path(self) -> str | None:
        return self._current_path

    def set_reload_request(self, request: ReloadRequest) -> None:
        self._reload_request = request

    def set_current_path(self, path: str | None) -> None:
        self._current_path = path

    async def put_updated_component_id(self, component_id: str) -> None:
        # Deduplicate: if a reload for this component is already queued, skip
        if component_id not in self._pending_component_ids:
            self._pending_component_ids.add(component_id)
            await self._queue.put(component_id)

    async def get_updated_component_id(self) -> str | None:
        component_id = await self._queue.get()
        self._pending_component_ids.discard(component_id)
        self._buffer.append(component_id)
        return component_id

    def get_missed_events(self, last_event: str) -> Generator[str, None, None]:
        idx = next(
            (i for i, item in enumerate(self._buffer) if item == last_event), -1
        )
        if idx == -1:
            # Buffer rolled over — client missed too many events, force full reload
            yield "__reload__"
            return
        for i, item in enumerate(self._buffer):
            if i > idx:
                yield item

    def add_component(self, component: "Component") -> None:
        self._components[str(id(component))] = component

    def get_component(self, component_id: str) -> "Component":
        return self._components[str(component_id)]

    @property
    def state_lock(self) -> asyncio.Lock:
        return self._state_lock

    def new_task_slot(self) -> asyncio.Event:
        if self._current_task_event and not self._current_task_event.is_set():
            self._current_task_event.set()
        self._current_task_event = asyncio.Event()
        return self._current_task_event


class SessionStorage:
    _sessions: ClassVar[dict[str, Session]] = {}
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    @classmethod
    async def get_session(cls, session_id: str) -> Session | None:
        # No lock needed: asyncio is single-threaded, dict reads are safe between awaits
        return cls._sessions.get(session_id)

    @classmethod
    async def create_session(
        cls, buffer_size: int = 10, component_ttl: float = 300
    ) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(session_id, buffer_size=buffer_size, component_ttl=component_ttl)

        async with cls._lock:
            cls._sessions[session_id] = session

        return session

    @classmethod
    async def delete_session(cls, session_id: str) -> None:
        # Check-and-delete inside the lock to avoid TOCTOU
        async with cls._lock:
            cls._sessions.pop(session_id, None)
