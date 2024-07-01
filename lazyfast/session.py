import asyncio, uuid
from typing import Type

from fastapi import Depends, HTTPException, Request

from lazyfast.component import Component
from lazyfast.state import State
from lazyfast.utils import generate_csrf_token


async def _load_form_data(request: Request) -> dict[str, str]:
    return dict(await request.form())


class ReloadRequest:
    def __init__(
        self, request: Request, inputs: dict[str, str] = Depends(_load_form_data)
    ) -> None:
        self._method = request.method
        self._session_id = request.state.session.id

        if self._method != "GET":
            csrf_token = inputs.get("csrf")

            if csrf_token != request.state.session.csrf_token:
                raise HTTPException(status_code=403, detail="Invalid CSRF token")

        self._trigger_id = inputs.get("__tid__")
        self._trigger_event = inputs.get("__evt__")

        if self._trigger_id:
            del inputs["__tid__"]
        if self._trigger_event:
            del inputs["__evt__"]
        self._data = inputs

        request.state.session.set_reload_request(self)

    @property
    def method(self) -> str:
        return self._method

    @property
    def trigger_id(self) -> str | None:
        return self._trigger_id

    @property
    def trigger_event(self) -> str | None:
        return self._trigger_event

    @property
    def data(self) -> dict[str, str] | None:
        return dict(self._data)

    @property
    def session_id(self) -> str:
        return self._session_id


class Session:
    def __init__(self, session_id: str, state: State | None = None) -> None:
        self._session_id = session_id
        self._queue = asyncio.Queue()
        self._components: dict[int, Type["Component"]] = {}
        self._csrf_token = generate_csrf_token()
        self._current_path = None
        self._reload_request = None

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

    def set_reload_request(self, request: ReloadRequest) -> None:
        self._reload_request = request

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
    async def create_session(state: Type[State] | None = None) -> Session:
        session_id = str(uuid.uuid4())

        async with SessionStorage.lock:
            session = Session(session_id, state)
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
