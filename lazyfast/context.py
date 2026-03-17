from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from asgiref.local import Local

if TYPE_CHECKING:
    from lazyfast.session import Session
    from lazyfast.tags import BaseHTML

local_data = Local()


# Работа с tag_stack
def get_all_tags_from_stack() -> list[BaseHTML]:
    return getattr(local_data, "tag_stack", [])


def append_tag_to_stack(elm: BaseHTML) -> None:
    if hasattr(local_data, "tag_stack"):
        local_data.tag_stack.append(elm)
    else:
        local_data.tag_stack = deque([elm])


def get_last_tag_from_stack() -> BaseHTML | None:
    if tag_stack := getattr(local_data, "tag_stack", None):
        return tag_stack[-1]
    return None


def update_last_tag_in_stack(elm: BaseHTML) -> None:
    if hasattr(local_data, "tag_stack"):
        local_data.tag_stack[-1] = elm


def pop_last_tag_from_stack() -> None:
    if hasattr(local_data, "tag_stack"):
        local_data.tag_stack.pop()


def clear_tag_stack() -> None:
    local_data.tag_stack = deque()


# Работа с root_tags
def get_root_tags() -> list[BaseHTML]:
    return getattr(local_data, "root_tags", [])


def clear_root_tags() -> None:
    local_data.root_tags = []


def add_root_tag(tag: BaseHTML) -> None:
    if not hasattr(local_data, "root_tags"):
        local_data.root_tags = []
    local_data.root_tags.append(tag)


# Работа с session
def set_session(session: Session) -> None:
    local_data.session = session


def get_session() -> Session:
    session = getattr(local_data, "session", None)
    if session is None:
        raise RuntimeError("No session in current context")
    return session


def enable_caching() -> None:
    local_data.caching = True


def is_caching_enabled() -> bool:
    return getattr(local_data, "caching", False)
