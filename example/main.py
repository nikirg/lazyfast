from asyncio import sleep
import asyncio
import random
from typing import Any, Literal, Type

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from pydantic import BaseModel

import pyfront as pf
from pyfront.state_manager.queue import StateQueue

GROUP_TYPE = Literal["internal", "external"]


class User(BaseModel):
    id: int
    name: str
    group: GROUP_TYPE


async def get_user_by_group(group: GROUP_TYPE) -> list[User]:
    await sleep(random.randint(1, 3))
    users = [
        User(id=1, name="John", group="external"),
        User(id=2, name="Alice", group="internal"),
        User(id=3, name="Anna", group="internal"),
        User(id=4, name="Sam", group="external"),
        User(id=5, name="Bob", group="internal"),
        User(id=6, name="Eve", group="external"),
        User(id=7, name="Mark", group="internal"),
        User(id=8, name="Kate", group="internal"),
        User(id=9, name="Tim", group="external"),
    ]
    return [user for user in users if user.group == group]


class State(pf.State):
    selected_user_group: GROUP_TYPE = "internal"
    info: str | None = None


class UserGroup(pf.Component):
    groups: list[str] = ["internal", "external"]

    async def view(self):
        dataset = {"htmx-indicator-class": "is-loading"}

        with pf.div(class_="field"):
            pf.label("Select user group", class_="label", for_="group")

            with pf.div(class_="control"):
                with pf.div(class_="select", dataset=dataset):
                    with pf.select(id="group", name="group") as group_select:
                        for group in self.groups:
                            pf.option(
                                group.capitalize(),
                                value=group,
                                selected=group == group_select.value,
                            )

        # if group_select.value:
        #     async with State() as state:
        #         state.selected_user_group = group_select.value

        # state = State(
        #     selected_user_group=group_select.value
        # )
        # await state.commit()


class UserList(pf.Component):
    group: GROUP_TYPE = "internal"

    async def view(self):
        users = await get_user_by_group(self.group)

        with pf.table(class_="table"):
            with pf.thead():
                with pf.tr():
                    pf.th("ID")
                    pf.th("Name")

            with pf.tbody():
                for user in users:
                    with pf.tr():
                        pf.td(user.id)
                        pf.td(user.name)


with open("example/test.js", "r", encoding="utf-8") as file:
    js_script = file.read()


class Page(pf.Component):
    title: str
    charset: str = "UTF-8"
    lang: str = "en"

    async def view(self):
        with pf.html(lang=self.lang):
            with pf.head():
                pf.meta(charset=self.charset)
                pf.title(self.title)
                pf.link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
                )
                pf.script(src="https://unpkg.com/htmx.org")
                pf.script(src="https://unpkg.com/htmx.org/dist/ext/sse.js")
                pf.script(js_script)

            with pf.body():
                with pf.div(hx=pf.HTMX(ext="sse", sse_connect="/__htmx__/stream")):
                    with pf.div(class_="container mt-6"):
                        with pf.div(class_="grid"):
                            with pf.div(class_="cell"):
                                with pf.div(class_="box"):
                                    #pf.HTMX.wrap(UserGroup())
                                    UserGroup()

                            with pf.div(class_="cell"):
                                with pf.div(class_="box"):
                                    #pf.HTMX.wrap(UserList())
                                    
                                    UserList()


app = FastAPI()
pf.init(app, "fake-secret")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    html = await Page(title="Pyfront").html(request)
    return html


queue = StateQueue()


components = [UserList]


@app.get("/__htmx__/stream", response_class=StreamingResponse)
async def stream(request: Request):
    async def event_stream():
        sid = request.session["id"]
        await queue.add(sid)
        try:
            while True:
                if await request.is_disconnected():
                    break
                await asyncio.sleep(0.5)
                component_id = await queue.dequeue(sid)
                yield f"event: cid_{component_id}\ndata: <none>\n\n"
        finally:
            await queue.delete(sid)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
