import asyncio
from typing import Type
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from renderable.state import State


SESSION_COOKIE_KEY = "sid"
SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 7


class Session:
    _state: State | None = None
    _queue: asyncio.Queue
    _session_id: str | None = None

    def __init__(self, session_id: str, state: State | None = None) -> None:
        self._session_id = session_id
        self._state = state
        self._queue = asyncio.Queue()

        if self._state:
            self._state.set_queue(self._queue)

    @property
    def id(self) -> str:
        return self._session_id

    @property
    def state(self) -> State:
        return self._state

    def set_state(self, state: State) -> None:
        self._state = state

    async def get_updated_component_id(self) -> str | None:
        if self._state:
            return await self._state.dequeue()


class SessionStorage:
    sessions: dict[str, Session] = {}
    lock: asyncio.Lock = asyncio.Lock()

    @staticmethod
    async def get_session(session_id: str) -> Session | None:
        async with SessionStorage.lock:
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


# class SessionMiddleware(BaseHTTPMiddleware):
#     async def dispatch(
#         self, request: Request, call_next: RequestResponseEndpoint
#     ) -> Response:
#         session_id = request.cookies.get(SESSION_COOKIE_KEY)
#         session = await self._get_or_create_session(request, session_id)
#         request.state.session = session
#         response = await call_next(request)

#         if not session_id or session_id != session.id:
#             response.set_cookie(
#                 key=SESSION_COOKIE_KEY,
#                 value=session.id,
#                 httponly=True,
#                 max_age=SESSION_COOKIE_MAX_AGE,
#             )
#         return response

#     async def _get_or_create_session(
#         self, request: Request, session_id: str | None
#     ) -> Session:
#         if session_id:
#             session = await SessionStorage.get_session(session_id)
#             if not session:
#                 state = request.app.state_schema()
#                 session = await SessionStorage.create_session(state)
#         else:
#             state = request.app.state_schema()
#             session = await SessionStorage.create_session(state)
#         return session
