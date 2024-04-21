from asyncio import sleep
import random
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

import pyfront as pf


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


class UserList(pf.Component):
    async def view(self):
        with pf.div(class_="field"):
            pf.label("Select user group", class_="label", for_="group")

            with pf.div(class_="control"):
                with pf.div(
                    class_="select", dataset={"htmx-indicator-class": "is-loading"}
                ):

                    with pf.select(id="group", name="group") as group_select:
                        for group in ("internal", "external"):
                            pf.option(
                                group.capitalize(),
                                value=group,
                                selected=group == group_select.value,
                            )

        users = await get_user_by_group(group_select.value or "internal")

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


with open("example/test.js", "r") as file:
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
                pf.script(src="https://unpkg.com/htmx.org@1.8.4")
                pf.script(js_script)

            with pf.body():
                with pf.div(class_="container mt-6"):
                    with pf.div(class_="grid"):
                        with pf.div(class_="cell"):
                            with pf.div(class_="box"):
                                pf.HTMX.wrap(UserList())

                        with pf.div(class_="cell"):
                            with pf.div(class_="box"):
                                pass


app = FastAPI()

pf.HTMX.configure(app)


@app.get("/")
async def root():
    page = Page(title="Pyfront")
    return HTMLResponse(await page.html())
