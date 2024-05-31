from fastapi import Depends, FastAPI
from renderable import RenderableRouter, State as BaseState, tags
from renderable.component import Component


class State(BaseState):
    tasks: list[str] = []


router = RenderableRouter(state_schema=State)


@router.component()
class TodoList(Component):
    async def view(self, state: State = Depends(State.load)):
        with tags.form():
            with tags.div(class_="box"):
                with tags.div(class_="field"):
                    tags.label("Task", class_="label", for_="task")
                    inp = tags.input(
                        class_="input", id="task", name="task", type_="text"
                    )

                with tags.div(class_="field"):
                    submit_btn = tags.button(
                        "Add", id="submit", class_="button", type_="button"
                    )

                    if submit_btn.trigger:
                        async with state:
                            state.tasks.append(inp.value)

                        inp.value = None

        for index, task in enumerate(state.tasks):
            with tags.div(class_="box is-flex is-justify-content-space-between"):
                tags.h2(f"{index + 1}. {task}")

                del_btn = tags.button("x", id=f"del_{index}", class_="button")

                if del_btn.trigger:
                    async with state:
                        state.tasks.pop(index)
                        await self.reload()


def extra_head():
    tags.title("Todo List")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.page("/", head=extra_head)
def root():
    with tags.div(class_="container mt-6"):
        TodoList()


app = FastAPI()
app.include_router(router)
