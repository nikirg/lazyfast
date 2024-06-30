import asyncio
from typing import Type
import uuid

from viewlet.component import Component
from viewlet.state import State


class Session:
    def __init__(
        self, session_id: str, state: State | None = None, csrf_token: str | None = None
    ) -> None:
        self._session_id = session_id
        self._queue = asyncio.Queue()
        self._components: dict[int, Type["Component"]] = {}
        self._csrf_token = csrf_token
        self._current_path = None

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
    def current_path(self) -> str | None:
        return self._current_path

    def set_current_path(self, path: str) -> None:
        self._current_path = path
        
        
    def set_state(self, state: State) -> None:
        self._state = state

    async def get_updated_component_id(self) -> str | None:
        if self._state:
            return await self._state.dequeue()

    def add_component(self, component: Type["Component"]) -> None:
        self._components[str(id(component))] = component

    def get_component(self, component_id: str) -> Type["Component"]:
        return self._components[str(component_id)]


class SessionStorage:
    sessions: dict[str, Session] = {}
    lock: asyncio.Lock = asyncio.Lock()

    @staticmethod
    async def get_session(session_id: str) -> Session | None:
        return SessionStorage.sessions.get(session_id)

    @staticmethod
    async def create_session(
        state: Type[State] | None = None, csrf_token: str | None = None
    ) -> Session:
        session_id = str(uuid.uuid4())

        async with SessionStorage.lock:
            session = Session(session_id, state, csrf_token)
            SessionStorage.sessions[session_id] = session
            return session

    @staticmethod
    async def update_session(session_id: str, data: dict) -> None:
        async with SessionStorage.lock:
            session = await SessionStorage.get_session(session_id)
            if session:
                session.set_data(data)

    @staticmethod
    async def delete_session(session_id: str) -> None:
        async with SessionStorage.lock:
            if session_id in SessionStorage.sessions:
                del SessionStorage.sessions[session_id]
