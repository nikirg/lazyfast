import contextvars
import json
from typing import Any, Literal, Type
from base64 import b64decode, b64encode
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.responses import Response
from itsdangerous import BadSignature
from pydantic import BaseModel
from starlette.datastructures import Secret
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import HTTPConnection

# from pyfront import state
from pyfront.component import Component
from pyfront.htmx import HTMX


# request_var = contextvars.ContextVar("request_var", default=None)


# class ComponentResponse(Response):
#     def __init__(self, component: Type[Component], **kwargs):
#         self.component = component
#         super().__init__(**kwargs)

#     async def __call__(self, scope, receive, send):
#         request = request_var.get()
#         print(self.component)
#         html_content = await self.component.html(request)
#         self.body = html_content.encode('utf-8')
#         self.headers['content-type'] = 'text/html'
#         await super().__call__(scope, receive, send)


class SessionIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.session.get("id") is None:
            request.session["id"] = str(uuid.uuid4())
        response = await call_next(request)
        return response


def init(app: FastAPI, secret_key: str, state_schema: Type[BaseModel] | None = None):
    app.add_middleware(SessionIdMiddleware)
    app.add_middleware(SessionMiddleware, secret_key=secret_key)
    
    HTMX.configure(app)
    
    # if state_schema:
    #     state_manager = StateManager[state_schema](state_schema)
    #     Component.configure(state_manager)


