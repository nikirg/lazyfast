from typing import Literal
from fastapi import Depends, FastAPI
from pydantic import BaseModel

from renderable import RenderableRouter, tags, Component, State as BaseState

GROUP_TYPE = Literal["internal", "external"]


class User(BaseModel):
    id: int
    name: str
    group: GROUP_TYPE


class State(BaseState):
    group: GROUP_TYPE = "internal"


async def get_user_by_group(state: State = Depends(State.load)) -> list[User]:
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
    return [user for user in users if user.group == state.group]


router = RenderableRouter(state_schema=State)


@router.component(id="userList", reload_on=[State.group])
class UserList(Component):
    async def view(self, users: list[User] = Depends(get_user_by_group)):
        with tags.table(class_="table"):
            with tags.thead():
                with tags.tr():
                    tags.th("ID")
                    tags.th("Name")

            with tags.tbody():
                for user in users:
                    with tags.tr():
                        tags.td(user.id)
                        tags.td(user.name)


@router.component(id="Demo")
class Demo(Component):
    async def view(self):
        tags.button("Reload", class_="button")


@router.component(id="UserGroup")
class UserGroup(Component):
    async def view(self, state: State = Depends(State.load)) -> None:
        groups: list[str] = ["internal", "external"]
        dataset = {"htmx-indicator-class": "is-loading"}

        with tags.div(class_="field"):
            tags.label("Select user group", class_="label", for_="group")

            with tags.div(class_="control"):
                with tags.div(class_="select", dataset=dataset):
                    with tags.select(id="group", name="group") as group_select:
                        for group in groups:
                            tags.option(
                                group.capitalize(),
                                value=group,
                                selected=group == group_select.value,
                            )

        if group_select.value:
            async with state:
                state.group = group_select.value

        Demo()


def extra_head():
    # rb.meta(charset="UTF-8")
    tags.title("Renderable demo")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.page("/", head=extra_head)
async def root():
    with tags.div(class_="container mt-6"):
        with tags.div(class_="grid"):
            with tags.div(class_="cell"):
                with tags.div(class_="box"):
                    UserGroup()

            with tags.div(class_="cell"):
                with tags.div(class_="box"):
                    UserList()


app = FastAPI()
app.include_router(router)
