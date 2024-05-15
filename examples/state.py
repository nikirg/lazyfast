from typing import Literal
from fastapi import Depends, FastAPI
from pydantic import BaseModel

import renderable as rb

GROUP_TYPE = Literal["internal", "external"]


class User(BaseModel):
    id: int
    name: str
    group: GROUP_TYPE


class State(rb.State):
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


router = rb.RenderableRouter(state_schema=State)


@router.component(id="userList", reload_on=[State.group])
async def UserList(users: list[User] = Depends(get_user_by_group)):
    with rb.table(class_="table"):
        with rb.thead():
            with rb.tr():
                rb.th("ID")
                rb.th("Name")

        with rb.tbody():
            for user in users:
                with rb.tr():
                    rb.td(user.id)
                    rb.td(user.name)


@router.component()
async def UserGroup(state: State = Depends(State.load)) -> None:
    groups: list[str] = ["internal", "external"]
    dataset = {"htmx-indicator-class": "is-loading"}

    with rb.div(class_="field"):
        rb.label("Select user group", class_="label", for_="group")

        with rb.div(class_="control"):
            with rb.div(class_="select", dataset=dataset):
                with rb.select(id="group", name="group") as group_select:
                    for group in groups:
                        rb.option(
                            group.capitalize(),
                            value=group,
                            selected=group == group_select.value,
                        )

    if group_select.value:
        async with state:
            state.group = group_select.value


def extra_head():
    # rb.meta(charset="UTF-8")
    rb.title("Renderable demo")
    rb.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.page("/{page_id}", head=extra_head)
async def root():
    with rb.div(class_="container mt-6"):
        with rb.div(class_="grid"):
            with rb.div(class_="cell"):
                with rb.div(class_="box"):
                    UserGroup()

            with rb.div(class_="cell"):
                with rb.div(class_="box"):
                    UserList()


app = FastAPI()
app.include_router(router)
