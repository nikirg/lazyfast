"""
LazyFast showcase — all examples in one app.

Run:
    uv run --with uvicorn --with aiohttp --with openai --with markdown \
           --with beautifulsoup4 -m examples.showcase
    open http://localhost:8000
"""

from fastapi import FastAPI

from lazyfast import LazyFastRouter, tags
from example.apps.shared import BULMA, EXAMPLES

from example.apps.todo import router as todo_router
from example.apps.btc import router as btc_router
from example.apps.search import router as search_router
from example.apps.users import router as users_router
from example.apps.files import router as files_router
from example.apps.converter import router as converter_router
from example.apps.chat import router as chat_router


home_router = LazyFastRouter(loader_route_prefix="/__lf_home__")


@home_router.page(
    "/",
    head_renderer=lambda: (
        tags.meta(charset="UTF-8"),
        tags.title("LazyFast Showcase"),
        tags.link(rel="stylesheet", href=BULMA),
    ),
)
def home():
    with tags.section(class_="hero is-dark"):
        with tags.div(class_="hero-body"):
            with tags.div(class_="container"):
                tags.p("⚡ LazyFast", class_="title")
                tags.p("Interactive examples — pick one to explore", class_="subtitle")

    with tags.section(class_="section"):
        with tags.div(class_="container"):
            with tags.div(class_="columns is-multiline"):
                for path, label in EXAMPLES:
                    with tags.div(class_="column is-one-third"):
                        with tags.div(class_="card"):
                            with tags.div(class_="card-content"):
                                tags.p(label, class_="title is-5")
                            with tags.footer(class_="card-footer"):
                                tags.a("Open →", class_="card-footer-item", href=path)


app = FastAPI(title="LazyFast Showcase")

app.include_router(home_router)
app.include_router(todo_router)
app.include_router(btc_router)
app.include_router(search_router)
app.include_router(users_router)
app.include_router(files_router)
app.include_router(converter_router)
app.include_router(chat_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_graceful_shutdown=1)
