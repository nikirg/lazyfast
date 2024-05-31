from fastapi import Depends, FastAPI
from renderable import RenderableRouter, State as BaseState, tags
from renderable.component import Component


class State(BaseState):
    clicked: set[tuple[int, int]] = set()


router = RenderableRouter(state_schema=State)


@router.component()
class Box(Component):
    i: int
    j: int

    async def view(self, state: State = Depends(State.load)):
        style = "width: 80px; height: 80px;"

        coords = (self.i + 1, self.j + 1)
        id = f"{self.i+1}.{self.j+1}"

        if coords in state.clicked:
            btn = tags.button(
                id=id,
                class_="box",
                style=style
                + "--bulma-box-shadow: inset 0 0.5em 1em -0.125em hsla(var(--bulma-scheme-h),var(--bulma-scheme-s),var(--bulma-scheme-invert-l),0.1);",
            )

            if btn.trigger:
                async with state:
                    state.clicked.remove(coords)
                    await self.reload()
        else:
            btn = tags.button(id=id, class_="box", style=style)
            if btn.trigger:
                async with state:
                    state.clicked.add(coords)
                    await self.reload()


@router.component()
class Playground(Component):
    async def view(self):
        for i in range(6):
            with tags.div(class_="columns"):
                for j in range(10):
                    with tags.div(class_="column"):
                        Box(i=i, j=j)


def extra_head():
    tags.title("Sapper")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.page("/", head=extra_head)
def root():
    with tags.div(class_="container mt-6"):
        Playground()


app = FastAPI()
app.include_router(router)
