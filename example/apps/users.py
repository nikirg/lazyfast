"""
User Form example.

Standalone:
    uv run --with uvicorn -m examples.users
    open http://localhost:8000/users
"""

from typing import Literal

from pydantic import BaseModel
from fastapi import Depends, FastAPI

from lazyfast import LazyFastRouter, BaseState, Component, tags
from example.shared import common_head, render_nav


GROUP_TYPE = Literal["internal", "external"]
GROUPS: list[str] = ["internal", "external"]


class User(BaseModel):
    id: int
    name: str
    group: GROUP_TYPE


class State(BaseState):
    group: GROUP_TYPE = "internal"
    users: list[User] = [
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


async def get_users_by_group(state: State = Depends(State)) -> list[User]:
    return [u for u in state.users if u.group == state.group]


router = LazyFastRouter(state_schema=State, loader_route_prefix="/__lf_users__")


@router.component(id="userList", reload_on=[State.group, State.users])
class UserList(Component):
    async def view(self, users: list[User] = Depends(get_users_by_group)):
        with tags.table(class_="table is-fullwidth is-striped"):
            with tags.thead():
                with tags.tr():
                    tags.th("ID")
                    tags.th("Name")
                    tags.th("Group")
            with tags.tbody():
                for user in users:
                    with tags.tr():
                        tags.td(str(user.id))
                        tags.td(user.name)
                        tags.td(user.group)


@router.component(id="UserFilter")
class UserFilter(Component):
    async def view(self, state: State = Depends(State)):
        with tags.div(class_="field"):
            tags.label("Filter by group", class_="label", for_="uf_group")
            with tags.div(class_="control"):
                with tags.div(class_="select"):
                    with tags.select(id="uf_group", name="uf_group") as sel:
                        for group in GROUPS:
                            tags.option(
                                group.capitalize(),
                                value=group,
                                selected=(group == (sel.value or state.group)),
                            )
        if sel.value:
            async with state:
                state.group = sel.value


@router.component()
class UserForm(Component):
    selected_group: GROUP_TYPE = "internal"

    async def view(self, state: State = Depends(State)):
        with tags.form():
            with tags.div(class_="field"):
                tags.label("Name", class_="label", for_="uf_name")
                name_input = tags.input(
                    class_="input", id="uf_name", name="uf_name", type_="text"
                )

            with tags.div(class_="field"):
                tags.label("Group", class_="label", for_="uf_form_group")
                with tags.div(class_="control"):
                    with tags.div(class_="select"):
                        with tags.select(id="uf_form_group", name="uf_form_group") as gs:
                            for group in GROUPS:
                                tags.option(
                                    group.capitalize(),
                                    value=group,
                                    selected=(group == (gs.value or self.selected_group)),
                                )
            if gs.value:
                self.selected_group = gs.value

            with tags.div(class_="field"):
                submit_btn = tags.button(
                    "Add User", id="uf_submit", class_="button is-primary", type_="button"
                )
                if submit_btn.trigger and name_input.value:
                    async with state:
                        state.users.append(
                            User(
                                id=len(state.users) + 1,
                                name=name_input.value,
                                group=self.selected_group,
                            )
                        )


@router.page("/users", head_renderer=lambda: common_head("User Form"))
async def page():
    render_nav("/users")
    with tags.div(class_="container mt-5"):
        with tags.div(class_="columns"):
            with tags.div(class_="column is-4"):
                with tags.div(class_="box"):
                    tags.p("Add User", class_="title is-5")
                    UserForm()
            with tags.div(class_="column is-2"):
                with tags.div(class_="box"):
                    tags.p("Filter", class_="title is-5")
                    UserFilter()
            with tags.div(class_="column"):
                with tags.div(class_="box"):
                    tags.p("Users", class_="title is-5")
                    UserList()


app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_graceful_shutdown=1)
