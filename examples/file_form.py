from fastapi import FastAPI

from lazyfast import LazyFastRouter, Component, tags


router = LazyFastRouter()


@router.component()
class Form(Component):
    async def view(self):
        with tags.form():
            with tags.div(class_="field"):
                with tags.div(class_="box"):
                    inp = tags.input(
                        type_="file",
                        name="resume",
                        id="resume",
                        reload_on=["change"],
                    )

        if file := inp.value:
            tags.h1(f"File: {file.filename}")


def head_renderer():
    tags.title("File Form")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.page("/", head_renderer=head_renderer)
def root():
    with tags.div(class_="container mt-6"):
        Form()


app = FastAPI()
app.include_router(router)
