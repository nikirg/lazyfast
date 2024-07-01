from fastapi import FastAPI
from lazyfast import LazyFastRouter, tags, Component


def search_cities(q: str) -> list[str]:
    cities = [
        "New York",
        "Los Angeles",
        "Chicago",
        "Houston",
        "Phoenix",
        "Paris",
        "London",
        "Berlin",
        "Moscow",
        "Tokyo",
        "Delhi",
        "Jakarta",
        "Seoul",
        "Shanghai",
        "Beijing",
        "Manila",
    ]
    return [city for city in cities if q.lower() in city.lower()]


router = LazyFastRouter()


@router.component()
class LiveSearch(Component):
    async def view(self):
        with tags.div(class_="box"):
            with tags.div(class_="field"):
                tags.label("City Search", class_="label", for_="task")
                inp = tags.input(
                    class_="input",
                    id="task",
                    name="task",
                    type_="text",
                    placeholder="London",
                    reload_on=["oninput"],
                )

        if inp.value:
            cities = search_cities(inp.value)

            if not cities:
                tags.h2("No results found")
            else:
                for i, city in enumerate(cities):
                    with tags.div(class_="box"):
                        tags.h2(f"{i+1}. {city}")


def extra_head():
    tags.title("Live Search")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.page("/", head=extra_head)
def root():
    with tags.div(class_="container mt-6"):
        LiveSearch()


app = FastAPI()
app.include_router(router)
