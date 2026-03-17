"""
File Upload example.

Standalone:
    uv run --with uvicorn -m examples.files
    open http://localhost:8000/files
"""

from fastapi import FastAPI

from lazyfast import LazyFastRouter, Component, tags
from example.apps.shared import common_head, render_nav


router = LazyFastRouter(loader_route_prefix="/__lf_files__")


@router.component()
class FileForm(Component):
    async def view(self):
        with tags.form():
            with tags.div(class_="box"):
                with tags.div(class_="field"):
                    tags.label("Upload a file", class_="label", for_="resume")
                    inp = tags.input(
                        type_="file", name="resume", id="resume", reload_on=["change"]
                    )

        if file := inp.file:
            with tags.div(class_="notification is-success is-light mt-3"):
                tags.p(f"File: {file.filename}")
                tags.p(f"Content-Type: {file.content_type}")


@router.page("/files", head_renderer=lambda: common_head("File Upload"))
def page():
    render_nav("/files")
    with tags.div(class_="container mt-5"):
        FileForm()


app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_graceful_shutdown=1)
