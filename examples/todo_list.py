from datetime import datetime
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel

from lazyfast import LazyFastRouter, BaseState, Component, ReloadRequest, tags


class Task(BaseModel):
    id: int
    description: str
    created_at: datetime = datetime.now()


class State(BaseState):
    tasks: list[Task] = []

    def delete_task_by_id(self, task_id: int):
        self.tasks = [task for task in self.tasks if task.id != task_id]


router = LazyFastRouter(state_schema=State)


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

                    warning = tags.div(class_="help is-danger")

                with tags.div(class_="field"):
                    submit_btn = tags.button(
                        "Add",
                        id="submit",
                        class_="button",
                        type_="submit",
                    )

        if submit_btn.trigger:
            async with state:
                if inp.value:
                    task = Task(id=len(state.tasks) + 1, description=inp.value)
                    state.tasks.append(task)
                else:
                    warning.content = "Task cannot be empty"

            inp.value = None

        for task in sorted(state.tasks, key=lambda t: t.id, reverse=True):
            with tags.div(class_="box is-flex is-justify-content-space-between"):
                with tags.div(style="padding-right: 0.5rem"):
                    tags.h2(f"{task.id}. {task.description}")

                    humand_readable_time = task.created_at.strftime("%d %b %Y %H:%M")
                    tags.span(humand_readable_time, class_="help is-info")

                del_btn = tags.button("x", id=f"del_{task.id}", class_="button")

            if del_btn.trigger:
                async with state:
                    state.delete_task_by_id(task.id)
                    await self.reload()


# @tags.cache(max_age=10, invalidate_on=[State.name])
def head_renderer():
    tags.title("Todo List")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.page("/", head_renderer=head_renderer)
def root():
    with tags.div(class_="container mt-6 px-3"):
        TodoList()


app = FastAPI()
app.include_router(router)
