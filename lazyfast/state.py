from .dataclass import DataClass

from fastapi import Request

class BaseState(DataClass):
    def __init__(self, request: Request):
        session = request.state.session
        super().__init__(**session.state_data)

class State(BaseState):
    link: str
 