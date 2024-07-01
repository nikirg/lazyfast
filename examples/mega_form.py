from datetime import datetime
from fastapi import Depends, FastAPI, Request, UploadFile
from pydantic import BaseModel

from viewlet import ViewletRouter, BaseState, Component, ReloadRequest, tags


router = ViewletRouter()


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

def extra_head():
    tags.title("Mega Form")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.page("/", head=extra_head)
def root():
    with tags.div(class_="container mt-6"):
        Form()


app = FastAPI()
app.include_router(router)
