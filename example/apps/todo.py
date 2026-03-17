"""
Todo List example.

Standalone:
    uv run --with uvicorn -m examples.todo
    open http://localhost:8000/todo
"""

from datetime import datetime

from pydantic import BaseModel
from fastapi import Depends, FastAPI

from lazyfast import LazyFastRouter, BaseState, Component, tags
from example.shared import common_head, render_nav


class Task(BaseModel):
    id: int
    description: str
    created_at: datetime = datetime.now()


class State(BaseState):
    tasks: list[Task] = []

    def delete_task_by_id(self, task_id: int) -> None:
        self.tasks = [t for t in self.tasks if t.id != task_id]


router = LazyFastRouter(state_schema=State, loader_route_prefix="/__lf_todo__")


@router.component()
class TodoList(Component):
    async def view(self, state: State = Depends(State)):
        with tags.form():
            with tags.div(class_="box"):
                with tags.div(class_="field"):
                    tags.label("Task", class_="label", for_="todo_task")
                    inp = tags.input(
                        class_="input", id="todo_task", name="todo_task", type_="text"
                    )
                    warning = tags.div(class_="help is-danger")

                with tags.div(class_="field"):
                    submit_btn = tags.button(
                        "Add", id="todo_submit", class_="button is-primary", type_="submit"
                    )
                    if submit_btn.trigger:
                        async with state:
                            if inp.value:
                                state.tasks.append(
                                    Task(id=len(state.tasks) + 1, description=inp.value)
                                )
                            else:
                                warning.content = "Task cannot be empty"
                        inp.value = None

        for task in sorted(state.tasks, key=lambda t: t.id, reverse=True):
            with tags.div(class_="box is-flex is-justify-content-space-between"):
                with tags.div(style="padding-right: 0.5rem"):
                    tags.p(f"{task.id}. {task.description}", class_="has-text-weight-medium")
                    tags.span(task.created_at.strftime("%d %b %Y %H:%M"), class_="help is-info")
                del_btn = tags.button("×", id=f"todo_del_{task.id}", class_="button is-small")
                if del_btn.trigger:
                    async with state:
                        state.delete_task_by_id(task.id)
                        await self.reload()


@router.page("/todo", head_renderer=lambda: common_head("Todo List"))
def page():
    render_nav("/todo")
    with tags.div(class_="container mt-5 px-3"):
        TodoList()


app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_graceful_shutdown=1)
