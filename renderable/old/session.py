import asyncio
import uuid
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class Session:
    def __init__(self, session_id: str, data: dict | None) -> None:
        self._session_id: str = session_id
        self._data: dict | None = data

    @property
    def id(self) -> str:
        return self._session_id

    @property
    def data(self) -> dict | None:
        return self._data

    def set_data(self, data: dict) -> None:
        self._data = data


class SessionStorage:
    sessions: dict[str, Session] = {}
    lock: asyncio.Lock = asyncio.Lock()

    @staticmethod
    async def get_session(session_id: str) -> Session | None:
        async with SessionStorage.lock:
            return SessionStorage.sessions.get(session_id)

    @staticmethod
    async def create_session(data: dict | None = None) -> Session:
        session_id = str(uuid.uuid4())

        async with SessionStorage.lock:
            session = Session(session_id, data)
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


SESSION_COOKIE_KEY = "sid"
SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 7


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if session_id := request.cookies.get(SESSION_COOKIE_KEY):
            session = await SessionStorage.get_session(session_id)
        else:
            session = await SessionStorage.create_session()

        request.state.session = session
        response = await call_next(request)

        if not request.cookies.get(SESSION_COOKIE_KEY):
            response.set_cookie(
                key=SESSION_COOKIE_KEY,
                value=session_id,
                httponly=True,
                max_age=SESSION_COOKIE_MAX_AGE,
            )

        return response
