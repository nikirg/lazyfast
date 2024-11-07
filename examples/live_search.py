from fastapi import Depends, FastAPI
from lazyfast import LazyFastRouter, tags, Component, BaseState


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


class State(BaseState):
    matched_cities: list[str] | None = None


router = LazyFastRouter(state_schema=State)


@router.component()
class LiveSearch(Component):
    async def view(self, state: State = Depends(State.load)):
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
            async with state:
                state.matched_cities = search_cities(inp.value)

@router.component(id="search-results", reload_on=[State.matched_cities])
class SearchResults(Component):
    async def view(self, state: State = Depends(State.load)):
        if mathed_cities := state.matched_cities:
            for i, city in enumerate(mathed_cities):
                with tags.div(class_="box"):
                    tags.h2(f"{i+1}. {city}")
        else:
            tags.h2("No results found")


def head_renderer():
    tags.title("Live Search")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.page("/", head_renderer=head_renderer)
def root():
    with tags.div(class_="container mt-6 px-3"):
        LiveSearch()
        with tags.div(class_="pt-3"):
            SearchResults()


app = FastAPI()
app.include_router(router)
