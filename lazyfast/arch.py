"""
- Router
    - SessionStorage
        - Session
          - ComponentStorage
            - ComponentState

          - StateManager
            - State
    
    - ComponentRegistry
        - ComponentClass
         
state_schema: Type[State] | None = None,
session_cookie_key: str = "sid",
session_cookie_max_age: int = 60 * 60 * 24 * 7,
session_delete_timeout: int = 10,
htmx_cdn: str = "https://unpkg.com/htmx.org",
loader_class: str = "__componentLoader__",
loader_route_prefix: str = "/__lazyfast__",
sse_endpoint_dependencies: Sequence[params.Depends] | None = None,
sse_tick_interval: float = 0.5,
sse_buffer_size: int = 10,
csrf_input_id: str = "csrf",
"""


class SessionStorage:
    def __init__(self):
        self.sessions = {}


class ComponentStorage:
    def __init__(self):
        self.component_instances = {}


class StateManager:
    def __init__(self):
        self.states = {}


class Session:
    def __init__(self):
        self.component_storage = ComponentStorage()
        self.state_manager = StateManager()


class ComponentRegistry:
    def __init__(self):
        self.components = {}


class Router:
    def __init__(self):
        self.session_storage = SessionStorage()
        self.component_registry = ComponentRegistry()
