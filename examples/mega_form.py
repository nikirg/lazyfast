from datetime import datetime
from fastapi import Depends, FastAPI, Request, File
from pydantic import BaseModel

from viewlet import ViewletRouter, BaseState, Component, ReloadRequest, tags


router = ViewletRouter()


@router.component()
class Form(Component):
    async def view(
        self,
        request: Request,
        reload_request: ReloadRequest = Depends(ReloadRequest),
        file: bytes = File(None, alias="resume"),
        
    ):
        with tags.form():
            with tags.div(class_="box"):
                inp = tags.input(
                    type_="file",
                    name="resume",
                    id="resume",
                    reload_on=["change"],
                )
                
                submit_btn = tags.button("Submit", class_="button", type_="submit")

        print(file)


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
