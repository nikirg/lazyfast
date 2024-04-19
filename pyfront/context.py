from contextvars import ContextVar

CURRENT_COMPONENT = ContextVar("current_component", default=None)
CURRENT_PARENT_ELEMENT = ContextVar("current_parent_element", default=None)
IS_HTMX_WRAPPER = ContextVar("is_htmx_wrapper", default=False)