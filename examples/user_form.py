from typing import Literal
from fastapi import Depends, FastAPI
from pydantic import BaseModel

from lazyfast import LazyFastRouter, tags, BaseState, Component

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


async def get_user_by_group(state: State = Depends(State.load)) -> list[User]:
    return [user for user in state.users if user.group == state.group]


router = LazyFastRouter(state_schema=State)


@router.component(id="userList", reload_on=[State.group, State.users])
class UserList(Component):
    async def view(self, users: list[User] = Depends(get_user_by_group)):
        with tags.table(class_="table"):
            with tags.thead():
                with tags.tr():
                    tags.th("ID")
                    tags.th("Name")
                    tags.th("Group")

            with tags.tbody():
                for user in users:
                    with tags.tr():
                        tags.td(user.id)
                        tags.td(user.name)
                        tags.td(user.group)

@router.component(id="Demo")
class Demo(Component):
    increment: int = 0

    async def view(self):
        self.increment += 1

        tags.button(self.increment, class_="button")


@router.component(id="UserFilter")
class UserFilter(Component):
    increment: int = 1

    async def view(self, state: State = Depends(State.load)) -> None:
        dataset = {"htmx-indicator-class": "is-loading"}

        with tags.div(class_="field"):
            tags.label("Select user group", class_="label", for_="group")

            with tags.div(class_="control"):
                with tags.div(class_="select", dataset=dataset):
                    with tags.select(id="group", name="group") as group_select:
                        for group in GROUPS:
                            tags.option(
                                group.capitalize(),
                                value=group,
                                selected=group == group_select.value,
                            )

        if group_select.value:
            async with state:
                state.group = group_select.value


@router.component()
class UserForm(Component):
    selected_group: GROUP_TYPE = "internal"

    async def view(self, state: State = Depends(State.load)) -> None:
        dataset = {"htmx-indicator-class": "is-loading"}

        with tags.form():
            with tags.div(class_="field"):
                tags.label("Name", class_="label", for_="name")
                name_input = tags.input(
                    class_="input", id="name", name="name", type_="text"
                )

            with tags.div(class_="field"):
                tags.label("Group", class_="label", for_="group")

                with tags.div(class_="control"):
                    with tags.div(class_="select", dataset=dataset):
                        with tags.select(id="group", name="group") as group_select:
                            for group in GROUPS:
                                tags.option(
                                    group.capitalize(),
                                    value=group,
                                    selected=group == group_select.value,
                                )

            if group_select.value:
                self.selected_group = group_select.value

            with tags.div(class_="field"):
                submit_btn = tags.button(
                    "Submit",
                    id="submit",
                    class_="button",
                    type_="button",
                    dataset=dataset,
                )

                trigger = submit_btn.trigger
                # tags.h1(trigger)

                if trigger:
                    user = User(
                        id=len(state.users) + 1,
                        name=name_input.value,
                        group=self.selected_group,
                    )

                    async with state:
                        state.users.append(user)


def head_renderer():
    tags.meta(charset="UTF-8")
    tags.title("Renderable demo")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.page("/", head_renderer=head_renderer)
async def root():
    with tags.div(class_="container mt-6 px-3"):
        with tags.div(class_="grid"):
            with tags.div(class_="cell"):
                with tags.div(class_="box"):
                    UserForm()

            with tags.div(class_="cell"):
                with tags.div(class_="box"):
                    UserFilter()

            with tags.div(class_="cell"):
                with tags.div(class_="box", style="transition: width 2s;"):
                    UserList()


app = FastAPI()
app.include_router(router)
