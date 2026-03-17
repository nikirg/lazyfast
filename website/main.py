from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Import components first — registers them on their routers at module load time
import website.components.home  # noqa: F401
import website.components.docs  # noqa: F401

from website.routers.home import home_router
from website.routers.docs import docs_router

app = FastAPI(title="LazyFast Docs", docs_url=None)

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)

app.include_router(home_router)
app.include_router(docs_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_graceful_shutdown=1)
