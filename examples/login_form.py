from typing import Literal
from fastapi import Depends, FastAPI
from pydantic import BaseModel

from viewlet import ViewletRouter, tags, BaseState
from viewlet.component import Component


class User(BaseModel):
    id: int
    email: str
    password: str


class State(BaseState):
    user: User | None = None


router = ViewletRouter(state_schema=State)


@router.component()
class UserList(Component):
    async def view(self, state: State = Depends(State.load)) -> None:
        

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
                #tags.h1(trigger)

                if trigger:
                    user = User(
                        id=len(state.users) + 1,
                        name=name_input.value,
                        group=self.selected_group,
                    )

                    async with state:
                        state.users.append(user)


def extra_head():
    tags.meta(charset="UTF-8")
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
                    UserForm()

            with tags.div(class_="cell"):
                with tags.div(class_="box"):
                    UserFilter()
  
            with tags.div(class_="cell"):
                with tags.div(class_="box"):
                    UserList()


app = FastAPI()
app.include_router(router)
