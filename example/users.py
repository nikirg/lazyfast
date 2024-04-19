from typing import Literal

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

import pyfront as pf

app = FastAPI()

GROUP_TYPE = Literal["internal", "external"]

class User(BaseModel):
    id: int
    name: str
    group: GROUP_TYPE

def get_user_by_group(group: GROUP_TYPE) -> list[User]:
    users = [
        User(id=1, name="John", group="external"),
        User(id=2, name="Alice", group="internal"),
        User(id=3, name="Anna", group="internal"),
        User(id=4, name="Sam", group="external")
    ]
    return [user for user in users if user.group == group]

class UserList(pf.Component):
    group: GROUP_TYPE

    async def view(self):
        users = get_user_by_group(self.group)

        for user in users:
            pass

class Page(pf.Component):
    title: str = "Pyfront example"

    async def view(self):
        pf.h1(self.title)

        pf.label("Select user group", for_="group")
        with pf.select(id="group", name="group") as group_select:
            pf.option("Internal", value="internal")
            pf.option("External", value="external")

        with pf.table():
            pf.HTMX.wrap(UserList(group=group_select.value))
            
            