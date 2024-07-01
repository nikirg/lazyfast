from asyncio import sleep
from fastapi import FastAPI, BackgroundTasks, Depends
from pydantic import BaseModel

from lazyfast import RenderableRouter, tags, Component

style = """
.popover {
    position: absolute;
    background-color: white;
    border: 1px solid #ccc;
    padding: 10px;
    display: none;
    z-index: 1000;
}
"""

router = RenderableRouter()


class Movie(BaseModel):
    id: int
    name: str
    genre: str
    year: int
    director: str


movies = [
    Movie(
        id=1,
        name="The Godfather",
        genre="Drama",
        year=1972,
        director="Francis Ford Coppola",
    ),
    Movie(
        id=2,
        name="The Godfather: Part II",
        genre="Drama",
        year=1974,
        director="Francis Ford Coppola",
    ),
    Movie(
        id=3,
        name="The Dark Knight",
        genre="Action",
        year=2008,
        director="Christopher Nolan",
    ),
    Movie(id=4, name="12 Angry Men", genre="Drama", year=1957, director="Sidney Lumet"),
    Movie(
        id=5,
        name="Schindler's List",
        genre="Drama",
        year=1993,
        director="Steven Spielberg",
    ),
    Movie(
        id=6,
        name="Pulp Fiction",
        genre="Crime",
        year=1994,
        director="Quentin Tarantino",
    ),
    Movie(
        id=7, name="Inception", genre="Action", year=2010, director="Christopher Nolan"
    ),
    Movie(id=8, name="Fight Club", genre="Drama", year=1999, director="David Fincher"),
    Movie(
        id=9, name="Forrest Gump", genre="Drama", year=1994, director="Robert Zemeckis"
    ),
    Movie(
        id=10,
        name="The Lord of the Rings: The Return of the King",
        genre="Action",
        year=2003,
        director="Peter Jackson",
    ),
    Movie(
        id=11, name="The Matrix", genre="Action", year=1999, director="Lana Wachowski"
    ),
    Movie(
        id=12,
        name="Star Wars: Episode V - The Empire Strikes Back",
        genre="Action",
        year=1980,
        director="Irvin Kershner",
    ),
]


def get_movies(
    skip: int = 0, limit: int = 10, filters: dict[str, str] = {}
) -> list[Movie]:
    filtered_movies = movies

    for key, value in filters.items():
        filtered_movies = [
            movie for movie in filtered_movies if getattr(movie, key) == value
        ]

    return filtered_movies[skip : skip + limit]


def extra_head():
    tags.title("Interactive Table")
    tags.style(style)
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.component()
class GenreFilter(Component):
    async def view(self) -> None:
        genres = sorted({movie.genre for movie in movies})
      
        for genre in genres:
            with tags.div(class_="field"):
                with tags.label(class_="checkbox"):
                    checked_box = tags.input(type_="checkbox", name=genre, value=genre, id=genre)
                    tags.span(genre)

@router.component(preload_content=lambda x: tags.h1("ХУЙ"))
class Table(Component):
    async def view(self):
        with tags.table(class_="table is-fullwidth"):
            with tags.thead():
                with tags.tr():
                    tags.th("Name")

                    with tags.th():
                        tags.button(
                            "Genre",
                            class_="button",
                            type_="button",
                            popovertarget="genre",
                        )
                        with tags.div(id="genre", class_="card", popover=True):
                            GenreFilter()

                    tags.th("Year")
                    tags.th("Director")

            with tags.tbody():
                for movie in movies:
                    with tags.tr():
                        tags.td(movie.name)
                        tags.td(movie.genre)
                        tags.td(movie.year)
                        tags.td(movie.director)


@router.page("/", head=extra_head)
def root():
    with tags.div(class_="container mt-6"):
        with tags.div(class_="grid"):
            with tags.div(class_="cell"):
                with tags.div(class_="box"):
                    Table()


app = FastAPI()
app.include_router(router)
