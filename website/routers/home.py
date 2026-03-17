from lazyfast import LazyFastRouter, BaseState, tags
from website.shared import head, site_nav


class HomeState(BaseState):
    selected: int = 0


home_router = LazyFastRouter(
    state_schema=HomeState,
    loader_route_prefix="/__lf_home__",
)

FEATURES = [
    ("🏷️", "Tag-based HTML",
     "Build HTML with Python functions — no Jinja2, no templates, no string concatenation."),
    ("⚡", "Reactive Components",
     "Define components that re-render automatically when state changes via HTMX + SSE."),
    ("🔒", "Pure Python State",
     "Declare state as a Pydantic-compatible class. No JavaScript required."),
    ("🔌", "FastAPI Native",
     "LazyFast is an APIRouter subclass — slot it into any FastAPI app."),
    ("🎯", "Zero JS Config",
     "Interactive UIs without writing a line of JavaScript."),
    ("📦", "Minimal Deps",
     "Only FastAPI, HTMX (CDN), and python-multipart."),
]

SNIPPETS = [
    """\
from lazyfast import tags

with tags.div(class_="card"):
    tags.h2("Hello, LazyFast!")
    tags.p("Build HTML in pure Python.")
    tags.a("Docs →", href="/docs", class_="link")
""",
    """\
@router.component(id="counter")
class Counter(Component):
    async def view(self, state=Depends(State)):
        tags.p(str(state.count), class_="value")

        inc = tags.button("+1", id="inc")
        if inc.trigger:
            async with state:
                state.count += 1
""",
    """\
class AppState(BaseState):
    user: str = ""
    count: int = 0
    items: list[str] = []

# Inject anywhere with FastAPI Depends
async def view(self, state: AppState = Depends(AppState)):
    tags.p(f"User: {state.user}")
""",
    """\
from fastapi import FastAPI
from lazyfast import LazyFastRouter

router = LazyFastRouter(state_schema=State)

# ... define components and pages ...

app = FastAPI()
app.include_router(router)
app.mount("/static", StaticFiles(directory="static"))
""",
    """\
# No JavaScript. No bundler. No npm.
# HTMX is loaded from CDN automatically.

@router.component()
class LiveSearch(Component):
    async def view(self):
        inp = tags.input(
            name="q",
            placeholder="Search…",
            reload_on=["oninput"],  # re-renders on every keystroke
        )
""",
    """\
# requirements / pyproject.toml
dependencies = [
    "fastapi",
    "python-multipart",
    "lazyfast",
]

# HTMX is loaded from CDN — zero npm, zero bundler.
""",
]


@home_router.page("/", head_renderer=head("Home", hljs=True))
def home():
    from website.components.home import FeaturesGrid

    site_nav("/")

    with tags.div(class_="hero"):
        tags.span("v2.0 — Now with SSE reactive state", class_="hero-badge")
        tags.h1("Build reactive web apps\nin pure Python")
        tags.p(
            "LazyFast combines FastAPI, HTMX, and a component model "
            "so you can ship interactive UIs without touching JavaScript.",
            class_="subtitle",
        )
        with tags.div(class_="hero-buttons"):
            tags.a("Get Started →", href="/docs", class_="btn-primary")
            tags.a(
                "View Examples",
                href="https://github.com/nikirg/lazyfast/tree/main/example",
                class_="btn-secondary",
            )

    with tags.div(class_="features"):
        tags.p("Why LazyFast", class_="features-eyebrow")
        tags.h2("Everything you need")
        tags.p("A batteries-included framework for server-side reactive UIs.")
        FeaturesGrid()

    with tags.div(class_="site-footer"):
        tags.p("Built with ❤️ using LazyFast · MIT License")
