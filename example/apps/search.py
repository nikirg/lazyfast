"""
Live Search example.

Standalone:
    uv run --with uvicorn -m examples.search
    open http://localhost:8000/search
"""

from fastapi import FastAPI

from lazyfast import LazyFastRouter, Component, tags
from example.shared import common_head, render_nav


CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Paris", "London", "Berlin", "Moscow", "Tokyo",
    "Delhi", "Jakarta", "Seoul", "Shanghai", "Beijing", "Manila",
]


def search_cities(q: str) -> list[str]:
    return [c for c in CITIES if q.lower() in c.lower()]


router = LazyFastRouter(loader_route_prefix="/__lf_search__")


@router.component()
class LiveSearch(Component):
    async def view(self):
        with tags.div(class_="box"):
            with tags.div(class_="field"):
                tags.label("City Search", class_="label", for_="search_city")
                inp = tags.input(
                    class_="input",
                    id="search_city",
                    name="search_city",
                    type_="text",
                    placeholder="London",
                    reload_on=["oninput"],
                )

        if inp.value:
            cities = search_cities(inp.value)
            if not cities:
                tags.p("No results found", class_="has-text-grey mt-3")
            else:
                for i, city in enumerate(cities):
                    with tags.div(class_="box py-2 mt-2"):
                        tags.p(f"{i + 1}. {city}")


@router.page("/search", head_renderer=lambda: common_head("Live Search"))
def page():
    render_nav("/search")
    with tags.div(class_="container mt-5"):
        LiveSearch()


app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_graceful_shutdown=1)
