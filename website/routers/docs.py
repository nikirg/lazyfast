from lazyfast import LazyFastRouter, BaseState, tags
from website.shared import head, site_nav


# ── State ─────────────────────────────────────────────────────────────────────

class DemoState(BaseState):
    greeter_name: str = ""
    state_count: int = 0
    append_count: int = 0


# ── Router ────────────────────────────────────────────────────────────────────

docs_router = LazyFastRouter(
    state_schema=DemoState,
    loader_route_prefix="/__lf_docs__",
)


# ── Navigation ────────────────────────────────────────────────────────────────

DOCS_NAV = [
    ("Getting started", [
        ("/docs",               "00", "Introduction"),
        ("/docs/how-it-works",  "01", "How it works"),
        ("/docs/quickstart",    "02", "Quick start"),
    ]),
    ("Router & Page", [
        ("/docs/router", "03", "Router"),
        ("/docs/page",   "04", "Page"),
    ]),
    ("Tags", [
        ("/docs/tags",       "05", "Tags"),
        ("/docs/attributes", "06", "Attributes"),
    ]),
    ("Components", [
        ("/docs/components",     "07", "Components"),
        ("/docs/reloading",      "08", "Reloading"),
        ("/docs/indicators",     "09", "Indicators"),
        ("/docs/reload-request", "10", "ReloadRequest"),
        ("/docs/container",      "11", "Container"),
    ]),
    ("State", [
        ("/docs/state", "12", "State"),
    ]),
]

# Flat ordered list for prev/next
DOCS_PAGES = [(url, title) for _, section in DOCS_NAV for url, _, title in section]


# ── Code snippets ─────────────────────────────────────────────────────────────

QUICKSTART_CODE = """\
from fastapi import FastAPI, Depends
from lazyfast import LazyFastRouter, BaseState, Component, tags


class State(BaseState):
    greeter_name: str = ""


router = LazyFastRouter(state_schema=State)


@router.component(id="greeter")
class Greeter(Component):
    async def view(self, state: State = Depends(State)):
        with tags.form():
            inp = tags.input(name="gname", placeholder="Ada Lovelace", type_="text")
            btn = tags.button("Say hello →", id="greet-btn")

            if btn.trigger:
                async with state:
                    state.greeter_name = inp.value or ""

        if state.greeter_name:
            tags.h2(f"Hello, {state.greeter_name}!")


@router.page("/")
def index():
    Greeter()


app = FastAPI()
app.include_router(router)
"""

ROUTER_CODE = """\
from fastapi import FastAPI
from lazyfast import LazyFastRouter

app = FastAPI()
router = LazyFastRouter()

app.include_router(router)
"""

MULTIPLE_ROUTERS_CODE = """\
# Each router gets a unique loader_route_prefix.
# Do NOT use FastAPI's prefix= parameter — it would break the
# internal SSE and component endpoints.

home_router    = LazyFastRouter(loader_route_prefix="/__lf_home__")
account_router = LazyFastRouter(loader_route_prefix="/__lf_account__")
admin_router   = LazyFastRouter(loader_route_prefix="/__lf_admin__")

app.include_router(home_router)
app.include_router(account_router)
app.include_router(admin_router)
"""

PAGE_CODE = """\
from fastapi import FastAPI
from lazyfast import LazyFastRouter, tags

router = LazyFastRouter()


@router.page("/")
def index(query: str | None = None):
    with tags.div():
        tags.h1("Hello, World!")
        tags.span(query or "No query provided")


app = FastAPI()
app.include_router(router)
# GET /?query=example → full HTML document with the div inside
"""

HEAD_RENDERER_CODE = """\
def cdn_head():
    tags.meta(charset="utf-8")
    tags.meta(name="viewport", content_="width=device-width, initial-scale=1")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3/dist/css/bootstrap.min.css",
    )
    tags.script(
        src="https://cdn.jsdelivr.net/npm/bootstrap@5.3/dist/js/bootstrap.bundle.min.js",
    )


@router.page("/", head_renderer=cdn_head)
def index():
    with tags.div(class_="container"):
        tags.span("This page uses Bootstrap")
"""

TAGS_CODE = """\
from lazyfast import Component, tags

COLOR_MAP = {
    "violet": ("#7c3aed", "#ede9fe", "#ddd6fe"),
    "blue":   ("#2563eb", "#eff6ff", "#bfdbfe"),
    "green":  ("#16a34a", "#f0fdf4", "#bbf7d0"),
    "amber":  ("#d97706", "#fffbeb", "#fde68a"),
    "rose":   ("#e11d48", "#fff1f2", "#fecdd3"),
}


@router.component(id="tags-demo")
class TagsDemo(Component):
    color: str = "violet"

    async def view(self):
        sel = tags.select(name="color", reload_on=["onchange"])
        with sel:
            for val in COLOR_MAP:
                tags.option(val.capitalize(), value=val, selected=(val == self.color))

        chosen = sel.value or self.color
        self.color = chosen
        text_c, bg_c, border_c = COLOR_MAP[chosen]

        with tags.div(style=f"background:{bg_c}; border:2px dashed {border_c}"):
            tags.h2("Hello, LazyFast!", style=f"color:{text_c}")
            tags.p("Build HTML in pure Python.", style=f"color:{text_c}")
"""

TAG_NESTING_CODE = """\
with tags.div(class_="box", id="box"):
    with tags.div(class_="content"):
        tags.h1("Hello, World!")
    with tags.div(class_="control"):
        tags.button("Click me!", id="btn")

# Leaf nodes: pass content as first positional argument
tags.p("Hello, world!")

# ⚠ Cannot combine text content and nesting on the same tag:
# with tags.div("Some text"):   # raises TypeError
#     tags.span("child")
"""

TAG_ATTRS_CODE = """\
# Python reserved words get a trailing underscore:
#   class_ → class    type_  → type    for_  → for
#   async_ → async    dir_   → dir     content_ → content

tags.input(type_="text", name="username")
tags.label("Name", for_="username")

# HTMX attributes (advanced):
from lazyfast.htmx import HTMX
hx = HTMX(url="/some/endpoint", method="post", trigger="reveal")
tags.div(hx=hx)
# → <div hx-post="/some/endpoint" hx-trigger="reveal"></div>

# data-* attributes via dataset:
tags.div(dataset={"custom-attribute": "value"})
# → <div data-custom-attribute="value"></div>
"""

UNSAFE_HTML_CODE = """\
@router.component(id="unsafe-html-demo")
class UnsafeHTMLDemo(Component):
    raw: bool = False

    async def view(self):
        safe_btn = tags.button("Escaped (safe)", id="safe-btn", class_="demo-btn secondary")
        raw_btn  = tags.button("Raw HTML",       id="raw-btn",  class_="demo-btn primary")

        if safe_btn.trigger: self.raw = False
        if raw_btn.trigger:  self.raw = True

        html = "<b>Bold</b>, <em>italic</em>, <span style='color:#7c3aed'>violet</span>"

        # default: html-escaped; allow_unsafe_html=True: rendered as-is
        tags.div(html, allow_unsafe_html=self.raw)
"""

CUSTOM_TAG_CODE = """\
from dataclasses import dataclass
from lazyfast.tags import Tag

@dataclass(slots=True)
class MyCustomTag(Tag):
    my_attribute: str | None = None
"""

COMPONENTS_CODE = """\
from lazyfast import Component, tags


@router.component(id="counter-demo")
class CounterDemo(Component):
    # Local state: session keeps the same instance across reloads
    count: int = 0

    async def view(self):
        tags.div(str(self.count), class_="counter-value")

        with tags.div(class_="demo-btns"):
            dec = tags.button("−", id="comp-dec", class_="demo-btn secondary")
            inc = tags.button("+", id="comp-inc", class_="demo-btn primary")
            rst = tags.button("↺", id="comp-rst", class_="demo-btn danger")

        if inc.trigger: self.count += 1
        if dec.trigger: self.count -= 1
        if rst.trigger: self.count = 0
"""

COMPONENT_PARAMS_CODE = """\
@router.component(id="params-demo")
class Card(Component):
    title: str = "My Card"
    edit: bool = False

    async def view(self):
        toggle = tags.button(
            "Switch to Edit" if not self.edit else "Done editing",
            id="toggle", class_="demo-btn primary",
        )
        if toggle.trigger:
            self.edit = not self.edit

        tags.h3(self.title, style="margin-top:1rem; font-weight:700;")

        if self.edit:
            with tags.form():
                inp  = tags.input(name="title", placeholder="New title…")
                save = tags.button("Save", id="save-title", class_="demo-btn secondary")
                if save.trigger and inp.value:
                    self.title = inp.value
        else:
            tags.p("Read-only mode", style="color:var(--muted); font-size:0.875rem;")


@router.page("/")
def index():
    Card(title="Hello", edit=False)
"""

VIEW_ENDPOINT_CODE = """\
from fastapi import Request

async def get_current_user(request: Request) -> str:
    return request.headers.get("X-User", "anonymous")


@router.component()
class UserGreeter(Component):
    async def view(self, user: str = Depends(get_current_user)):
        tags.p(f"Hello, {user}!")
"""

TAG_INTERACTIVITY_CODE = """\
# Override or add events with reload_on:
tags.input(name="q", reload_on=["oninput", "keydown"])

# Use trigger to detect which element caused the current reload.
# The tag MUST have an id attribute.
btn = tags.button("Submit", id="submit_btn")
if btn.trigger:
    tags.div("Button was clicked")

inp = tags.input(type_="text", id="search", name="q")
if inp.trigger:
    tags.div(f"Triggered by: {inp.trigger}")  # e.g. "change"

# Wrap inputs in tags.form() to suppress their auto-reload.
# Only the submit button triggers a reload.
with tags.form():
    tags.input(name="q")              # does NOT auto-reload
    btn = tags.button("Go", id="go")
    if btn.trigger:
        tags.div("Searching…")
"""

SEARCH_CODE = """\
from lazyfast import Component, tags

FRAMEWORKS = ["FastAPI", "Django", "Flask", "Starlette",
              "Litestar", "Tornado", "Falcon", "Sanic"]


@router.component(id="search-demo")
class LiveSearchDemo(Component):
    async def view(self):
        inp = tags.input(
            name="q",
            placeholder="Filter frameworks…",
            reload_on=["oninput"],
        )

        query = (inp.value or "").lower()
        results = [f for f in FRAMEWORKS if query in f.lower()]

        with tags.div(class_="search-results"):
            for name in results:
                with tags.div(class_="search-item"):
                    tags.span("→", class_="search-item-icon")
                    tags.span(name)
            if not results:
                tags.p("No results found.", class_="search-empty")
"""

FORMS_CODE = """\
from lazyfast import Component, tags


@router.component(id="form-demo")
class FormsDemo(Component):
    async def view(self):
        feedback = tags.div()

        with tags.form():
            name_inp  = tags.input(name="fname",  placeholder="Ada Lovelace",    type_="text")
            email_inp = tags.input(name="femail", placeholder="ada@example.com", type_="email")
            msg_inp   = tags.input(name="fmsg",   placeholder="Hello!",          type_="text")
            btn = tags.button("Send message →", id="form-send")

            if btn.trigger:
                fname  = name_inp.value  or ""
                femail = email_inp.value or ""
                fmsg   = msg_inp.value   or ""
                if fname and femail and fmsg:
                    feedback.content = f"✓ Thanks {fname}! We'll reply to {femail}."
                    feedback.class_ = "form-success"
                else:
                    feedback.content = "✗ Please fill in all fields."
                    feedback.class_ = "form-error"
"""

STATE_FIELD_CHANGES_CODE = """\
@router.component(id="display", reload_on=[AppState.count])
class Display(Component):
    async def view(self, state: AppState = Depends(AppState)):
        tags.span(str(state.count))


@router.component(id="controls")
class Controls(Component):
    async def view(self, state: AppState = Depends(AppState)):
        btn = tags.button("Increment", id="inc_btn")
        if btn.trigger:
            async with state:
                state.count += 1

# When Controls commits state.count, Display reloads via SSE.
"""

SELF_RELOAD_CODE = """\
import asyncio, random


@router.component(id="self-reload-demo")
class SelfReloadDemo(Component):
    running: bool = False
    value: int = 0

    async def view(self):
        with tags.div(class_="demo-btns"):
            start = tags.button("Start", id="start-btn", class_="demo-btn primary")
            stop  = tags.button("Stop",  id="stop-btn",  class_="demo-btn secondary")

        if start.trigger: self.running = True
        if stop.trigger:  self.running = False

        if self.running:
            self.value = random.randint(0, 999)

        tags.div(str(self.value) if self.running else "—", class_="counter-value")

        if self.running:
            await asyncio.sleep(1)
            await self.reload()
"""

INDICATORS_CODE = """\
@router.component(id="indicator-demo")
class IndicatorDemo(Component):
    result: str = ""

    async def view(self):
        btn = tags.button(
            "Run slow operation",
            id="run-btn", class_="demo-btn primary",
            dataset={"htmx-indicator-class": "is-loading"},
        )
        # Hidden by default; shown while the POST is in-flight
        tags.span(" Processing…", is_indicator=True,
                  style="color:var(--muted); font-size:0.875rem;")

        if btn.trigger:
            await asyncio.sleep(1.5)
            self.result = "Done! Operation completed."

        if self.result:
            tags.div(self.result, class_="form-success", style="margin-top:1rem;")
"""

RELOAD_REQUEST_CODE = """\
from lazyfast import ReloadRequest


@router.component(id="reload-request-demo")
class ReloadRequestDemo(Component):
    async def view(self, req: ReloadRequest = Depends(ReloadRequest)):
        with tags.div(class_="demo-btns"):
            tags.button("Button A", id="btn-a", class_="demo-btn primary")
            tags.button("Button B", id="btn-b", class_="demo-btn secondary")
            tags.button("Button C", id="btn-c", class_="demo-btn danger")

        rows = [
            ("trigger_id",    req.trigger_id    or "—"),
            ("trigger_event", req.trigger_event or "—"),
            ("method",        req.method),
            ("session_id",    (req.session_id or "")[:8] + "…"),
        ]
        for key, val in rows:
            with tags.div(class_="req-row"):
                tags.span(key, class_="req-key")
                tags.span(val, class_="req-val")
"""

CONTAINER_CODE = """\
# preload_renderer — shown while the component loads:
@router.component(
    class_="my-class",
    preload_renderer=lambda: tags.div("Loading…"),
)
class MyComponent(Component):
    async def view(self):
        tags.div("Loaded!")


# swapping_method="append" — each render appends instead of replacing:
@router.component(id="append-list", swapping_method="append",
                  reload_on=[State.append_count])
class AppendList(Component):
    async def view(self, state: State = Depends(State)):
        tags.div(f"Item {state.append_count}", class_="search-item")


@router.component(id="append-trigger")
class AppendTrigger(Component):
    async def view(self, state: State = Depends(State)):
        btn = tags.button("Add item", id="add-item", class_="demo-btn primary")
        if btn.trigger:
            async with state:
                state.append_count += 1
"""

STATE_CODE = """\
from lazyfast import BaseState, Component, tags
from fastapi import Depends


class DemoState(BaseState):
    state_count: int = 0


@router.component(id="state-display", reload_on=[DemoState.state_count])
class StateDisplay(Component):
    async def view(self, state: DemoState = Depends(DemoState)):
        with tags.div(class_="state-comp"):
            tags.p("Display", class_="state-comp-label")
            tags.p(str(state.state_count), class_="state-comp-value")


@router.component(id="state-controls")
class StateControls(Component):
    async def view(self, state: DemoState = Depends(DemoState)):
        with tags.div(class_="state-comp"):
            tags.p("Controls", class_="state-comp-label")
            with tags.div(class_="state-controls"):
                dec = tags.button("−", id="state-dec", class_="demo-btn secondary")
                inc = tags.button("+", id="state-inc", class_="demo-btn primary")
                rst = tags.button("↺", id="state-rst", class_="demo-btn danger")

        if inc.trigger:
            async with state:
                state.state_count += 1
        if dec.trigger:
            async with state:
                state.state_count -= 1
        if rst.trigger:
            async with state:
                state.state_count = 0
"""


# ── Rendering helpers ──────────────────────────────────────────────────────────

def _code_panel(code: str, filename: str = "example.py") -> None:
    with tags.div(class_="code-panel"):
        with tags.div(class_="panel-header"):
            with tags.span(class_="panel-dots"):
                tags.span(class_="dot red")
                tags.span(class_="dot yellow")
                tags.span(class_="dot green")
            tags.span(filename, class_="panel-filename")
        with tags.pre():
            tags.code(code, class_="language-python")


def _live_panel(component_fn) -> None:
    with tags.div(class_="live-panel"):
        with tags.div(class_="live-header"):
            tags.span(class_="live-dot")
            tags.span("Live demo")
        with tags.div(class_="live-body"):
            component_fn()


def _section_header(badge: str, title: str) -> None:
    tags.span(badge, class_="section-badge")
    tags.h2(title)


def _ref_table(headers: list[str], rows: list[list[str]]) -> None:
    with tags.div(class_="ref-table-wrap"):
        with tags.table(class_="ref-table"):
            with tags.thead():
                with tags.tr():
                    for h in headers:
                        tags.th(h)
            with tags.tbody():
                for row in rows:
                    with tags.tr():
                        for i, cell in enumerate(row):
                            tags.td(cell, class_="mono" if i == 0 else None)


def _note(text: str) -> None:
    with tags.div(class_="doc-note"):
        tags.span("ℹ", class_="doc-note-icon")
        tags.span(text)


def _warn(text: str) -> None:
    with tags.div(class_="doc-warn"):
        tags.span("⚠", class_="doc-warn-icon")
        tags.span(text)


def _sidebar(current: str) -> None:
    with tags.aside(class_="sidebar"):
        for group_title, items in DOCS_NAV:
            with tags.div(class_="sidebar-section"):
                tags.h4(group_title)
                for url, num, title in items:
                    cls = "active" if url == current else ""
                    with tags.a(href=url, class_=cls):
                        tags.span(num, class_="num")
                        tags.span(title)


def _pagination(current: str) -> None:
    idx = next((i for i, (url, _) in enumerate(DOCS_PAGES) if url == current), 0)
    prev = DOCS_PAGES[idx - 1] if idx > 0 else None
    nxt  = DOCS_PAGES[idx + 1] if idx < len(DOCS_PAGES) - 1 else None

    with tags.div(class_="docs-pagination"):
        if prev:
            with tags.a(href=prev[0], class_="pagination-prev"):
                tags.span("←", class_="pagination-arrow")
                with tags.span(class_="pagination-label"):
                    tags.span("Previous", class_="pagination-hint")
                    tags.span(prev[1], class_="pagination-title")
        else:
            tags.div()
        if nxt:
            with tags.a(href=nxt[0], class_="pagination-next"):
                with tags.span(class_="pagination-label"):
                    tags.span("Next", class_="pagination-hint")
                    tags.span(nxt[1], class_="pagination-title")
                tags.span("→", class_="pagination-arrow")
        else:
            tags.div()


def _docs_page(current: str, content_fn) -> None:
    site_nav("/docs")
    with tags.div(class_="docs-wrapper"):
        _sidebar(current)
        with tags.div(class_="docs-content"):
            content_fn()
            _pagination(current)
    with tags.div(class_="site-footer"):
        with tags.p():
            tags.span("Built with LazyFast · MIT License · ")
            tags.a("GitHub", href="https://github.com/nikirg/lazyfast")


# ── Page content functions ─────────────────────────────────────────────────────

def _intro_content():
    with tags.div(class_="docs-intro"):
        tags.h1("Documentation")
        tags.p(
            "LazyFast is a Python framework that layers a component model and "
            "server-sent events on top of FastAPI. You declare state, wire up "
            "components, and the framework handles HTMX swapping and SSE "
            "broadcasts automatically."
        )
        tags.p(
            "No JavaScript configuration. No template language. "
            "Just Python classes, async functions, and the tags module for HTML."
        )
    with tags.div(class_="docs-index"):
        for group_title, items in DOCS_NAV:
            with tags.div(class_="index-group"):
                tags.h3(group_title, class_="index-group-title")
                with tags.div(class_="index-links"):
                    for url, num, title in items:
                        with tags.a(href=url, class_="index-link"):
                            tags.span(num, class_="index-num")
                            tags.span(title)


def _how_it_works_content():
    _section_header("01 · Getting started", "How LazyFast works")
    tags.p("Here is what happens when a user opens a LazyFast page:", class_="desc")
    with tags.ol(class_="how-it-works-list"):
        tags.li(
            "The browser requests the page — FastAPI returns a full HTML document "
            "with HTMX and LazyFast's JS included."
        )
        tags.li(
            "Each component on the page renders as an empty div with HTMX attributes. "
            "HTMX immediately fires a POST request to load the component's content."
        )
        tags.li(
            "The server runs the component's view() method and returns the rendered "
            "HTML fragment. HTMX swaps it in — no full reload."
        )
        tags.li(
            "When the user interacts (clicks a button, types in an input), HTMX fires "
            "another POST to re-render only that component, sending all current input "
            "values. The component re-runs view() with fresh data."
        )
        tags.li(
            "For background-driven updates (e.g. a live feed), a persistent "
            "Server-Sent Events (SSE) connection tells the browser which component IDs "
            "to reload."
        )
    tags.p(
        "You write only Python — no JavaScript needed for most use cases.",
        class_="desc",
        style="margin-top:1rem;",
    )


def _quickstart_content():
    from website.components.docs import GreeterDemo

    _section_header("02 · Getting started", "Quick start")
    tags.p(
        "Install LazyFast alongside FastAPI, create a router, define a component, "
        "and mount everything onto a FastAPI app. Run with uvicorn — that's it.",
        class_="desc",
    )
    with tags.div(class_="demo-grid"):
        _code_panel(QUICKSTART_CODE, "main.py")
        _live_panel(GreeterDemo)


def _router_content():
    _section_header("03 · Router & Page", "Application router")
    tags.p(
        "LazyFast is a FastAPI APIRouter subclass. Attach it with "
        "include_router — pages and components are then registered on the router.",
        class_="desc",
    )
    _code_panel(ROUTER_CODE, "main.py")

    tags.h3("Multiple routers", class_="subsection-title")
    tags.p(
        "Split a large app into independent sections — each router manages its own "
        "sessions and state. Each must have a unique loader_route_prefix.",
        class_="desc",
    )
    _code_panel(MULTIPLE_ROUTERS_CODE, "main.py")
    _warn(
        "Do not use FastAPI's prefix= parameter on a LazyFastRouter. "
        "The internal SSE and component endpoints use loader_route_prefix as an "
        "absolute path — a FastAPI prefix would break them."
    )


def _page_content():
    _section_header("04 · Router & Page", "Page")
    tags.p(
        "A page is a FastAPI endpoint decorated with @router.page(path). "
        "LazyFast wraps the output in a full HTML document with HTMX and its JS injected. "
        "You do not return anything — all tags are collected automatically.",
        class_="desc",
    )
    _code_panel(PAGE_CODE, "main.py")

    tags.h3("Custom scripts and styles", class_="subsection-title")
    tags.p(
        "Use head_renderer to inject meta, link, and script tags into the <head>. "
        "Pass any zero-argument callable.",
        class_="desc",
    )
    _code_panel(HEAD_RENDERER_CODE, "main.py")


def _tags_content():
    from website.components.docs import TagsDemo

    _section_header("05 · Tags", "Tags")
    tags.p(
        "Every HTML element is a Python callable in the tags module. "
        "Use it as a context manager to nest children, or pass content as "
        "the first positional argument for leaf nodes. "
        "HTML-special characters are escaped automatically.",
        class_="desc",
    )
    with tags.div(class_="demo-grid"):
        _code_panel(TAGS_CODE)
        _live_panel(TagsDemo)

    tags.h3("Nesting", class_="subsection-title")
    tags.p(
        "Use with to nest tags. Text content and nesting cannot be combined on the same tag.",
        class_="desc",
    )
    _code_panel(TAG_NESTING_CODE)


def _attributes_content():
    from website.components.docs import UnsafeHTMLDemo

    _section_header("06 · Tags", "Attributes")
    tags.p(
        "Almost all HTML attributes are supported as keyword arguments. "
        "A few names use a trailing underscore to avoid Python reserved words:",
        class_="desc",
    )
    _ref_table(
        ["Python argument", "HTML attribute"],
        [
            ["class_",   "class"],
            ["type_",    "type"],
            ["for_",     "for"],
            ["async_",   "async"],
            ["dir_",     "dir"],
            ["content_", "content"],
        ],
    )
    tags.p("HTMX integration and dataset for data-* attributes:", class_="desc", style="margin-top:1.25rem;")
    _code_panel(TAG_ATTRS_CODE)

    tags.h3("allow_unsafe_html", class_="subsection-title")
    tags.p(
        "By default text content is HTML-escaped. "
        "Set allow_unsafe_html=True to render a raw HTML string inside a tag.",
        class_="desc",
    )
    with tags.div(class_="demo-grid"):
        _code_panel(UNSAFE_HTML_CODE)
        _live_panel(UnsafeHTMLDemo)
    _warn(
        "Only use allow_unsafe_html=True with content you fully control. "
        "Never pass user-supplied strings with this flag."
    )

    tags.h3("Custom tags", class_="subsection-title")
    tags.p("If a tag you need is missing, subclass Tag and add your attributes:", class_="desc")
    _code_panel(CUSTOM_TAG_CODE)


def _components_content():
    from website.components.docs import CounterDemo, ComponentParamsDemo

    _section_header("07 · Components", "Components")
    tags.p(
        "A component is a class with a view() method, registered with "
        "@router.component(). It renders as a lazy-loaded HTMX endpoint. "
        "Component fields persist across reloads — the session holds the same instance.",
        class_="desc",
    )
    with tags.div(class_="demo-grid"):
        _code_panel(COMPONENTS_CODE)
        _live_panel(CounterDemo)

    tags.h3("Parameters", class_="subsection-title")
    tags.p(
        "Component fields also serve as configuration parameters passed when placing "
        "the component in a page. The same fields persist as local state across reloads.",
        class_="desc",
    )
    with tags.div(class_="demo-grid"):
        _code_panel(COMPONENT_PARAMS_CODE)
        _live_panel(ComponentParamsDemo)

    tags.h3("View as FastAPI endpoint", class_="subsection-title")
    tags.p(
        "view() is a full FastAPI endpoint and supports Depends injection — "
        "inject database sessions, current user, config, etc.",
        class_="desc",
    )
    _code_panel(VIEW_ENDPOINT_CODE)


def _reloading_content():
    from website.components.docs import LiveSearchDemo, FormsDemo, SelfReloadDemo

    _section_header("08 · Components", "Reloading")
    tags.p(
        "When a reload is triggered, the browser sends a POST to the component's "
        "view endpoint. The component re-runs and returns fresh HTML. "
        "All current input values are included automatically.",
        class_="desc",
    )

    tags.h3("Tag interactivity", class_="subsection-title")
    tags.p("These tags trigger a component reload automatically when the user interacts:", class_="desc")
    _ref_table(
        ["Tag", "Default event"],
        [
            ["input",                    "change"],
            ["button",                   "click"],
            ["select",                   "change"],
            ["textarea",                 "input"],
            ["input(type_=\"radio\")",   "click"],
            ["input(type_=\"checkbox\")", "change"],
        ],
    )
    tags.p("Use reload_on, trigger, and form suppression:", class_="desc", style="margin-top:1.25rem;")
    _code_panel(TAG_INTERACTIVITY_CODE)

    tags.h3("Live search (reload_on=[\"oninput\"])", class_="subsection-title")
    tags.p(
        "The component re-renders on every keystroke. "
        "inp.value is available immediately — no state persistence needed.",
        class_="desc",
    )
    with tags.div(class_="demo-grid"):
        _code_panel(SEARCH_CODE)
        _live_panel(LiveSearchDemo)

    tags.h3("Forms", class_="subsection-title")
    tags.p(
        "Wrap inputs and a submit button in tags.form(). "
        "Field values are accessible via inp.value after the button trigger fires.",
        class_="desc",
    )
    with tags.div(class_="demo-grid"):
        _code_panel(FORMS_CODE)
        _live_panel(FormsDemo)

    tags.h3("State field changes (SSE)", class_="subsection-title")
    tags.p(
        "A component subscribes to a state field via reload_on=[State.field]. "
        "When that field is committed, the component reloads via SSE — no polling.",
        class_="desc",
    )
    _code_panel(STATE_FIELD_CHANGES_CODE)
    _note("The component must have an explicit id when using reload_on with state fields.")

    tags.h3("Self reloading", class_="subsection-title")
    tags.p(
        "A component can push a reload to itself via await self.reload(). "
        "Useful for live-updating displays: clocks, prices, progress bars.",
        class_="desc",
    )
    with tags.div(class_="demo-grid"):
        _code_panel(SELF_RELOAD_CODE)
        _live_panel(SelfReloadDemo)


def _indicators_content():
    from website.components.docs import IndicatorDemo

    _section_header("09 · Components", "Indicators")
    tags.p(
        "While a component waits for a server response, show the user a loading "
        "state. Two approaches — they can be combined.",
        class_="desc",
    )
    _ref_table(
        ["Approach", "Behaviour"],
        [
            ["is_indicator=True",              "Tag is hidden by default; shown while the POST is in-flight"],
            ["data-htmx-indicator-class: foo", "Adds CSS class foo to the tag while reloading"],
        ],
    )
    with tags.div(class_="demo-grid", style="margin-top:1.25rem;"):
        _code_panel(INDICATORS_CODE)
        _live_panel(IndicatorDemo)


def _reload_request_content():
    from website.components.docs import ReloadRequestDemo

    _section_header("10 · Components", "ReloadRequest")
    tags.p(
        "Every reload carries a ReloadRequest with metadata about what triggered it. "
        "Inject it via Depends to branch logic before any tags render.",
        class_="desc",
    )
    _ref_table(
        ["Property", "Type", "Description"],
        [
            ["method",        "str",        "\"GET\" or \"POST\""],
            ["trigger_id",    "str | None", "id of the tag that triggered the reload"],
            ["trigger_event", "str | None", "JavaScript event name (e.g. \"click\")"],
            ["inputs",        "dict",       "Current values of all inputs in the component"],
            ["session_id",    "str",        "Unique ID for the current user session"],
        ],
    )
    with tags.div(class_="demo-grid", style="margin-top:1.25rem;"):
        _code_panel(RELOAD_REQUEST_CODE)
        _live_panel(ReloadRequestDemo)


def _container_content():
    from website.components.docs import AppendTrigger, AppendList

    _section_header("11 · Components", "Container customization")
    tags.p(
        "The @router.component() decorator accepts optional arguments that control "
        "the wrapper div and how content is swapped.",
        class_="desc",
    )
    _ref_table(
        ["Parameter", "Description"],
        [
            ["class_",           "CSS class added to the wrapper div"],
            ["preload_renderer", "Zero-argument callable rendered before the component loads"],
            ["swapping_method",  "\"replace\" (default), \"append\", or \"prepend\""],
        ],
    )
    tags.p(
        "swapping_method=\"append\" demo — each render appends instead of replacing. "
        "AppendList is triggered via SSE when append_count changes.",
        class_="desc",
        style="margin-top:1.25rem;",
    )
    with tags.div(class_="demo-grid"):
        _code_panel(CONTAINER_CODE)
        with tags.div(class_="live-panel"):
            with tags.div(class_="live-header"):
                tags.span(class_="live-dot")
                tags.span("Live demo")
            with tags.div(class_="live-body"):
                AppendTrigger()
                with tags.div(class_="search-results", style="margin-top:1rem; max-height:180px; overflow-y:auto;"):
                    AppendList()
                tags.p("Items accumulate — refresh page to clear", class_="sse-note")


def _state_content():
    from website.components.docs import StateDisplay, StateControls

    _section_header("12 · State", "State")
    tags.p(
        "Subclass BaseState to define session-scoped state. "
        "Each user session has its own isolated instance. "
        "Fields can be any serializable type.",
        class_="desc",
    )
    tags.p(
        "Mutate state inside async with state: — acquires a lock, commits atomically, "
        "then broadcasts SSE events to subscribed components. "
        "On exception, the lock releases without saving partial changes.",
        class_="desc",
    )
    _note(
        "Pessimistic locking: when you enter async with state, the state is locked "
        "to your session until the block exits — preventing race conditions in "
        "multi-component interactions."
    )
    tags.p(
        "Controls and Display are independent components. "
        "SSE is the only coupling between them.",
        class_="desc",
        style="margin-top:1rem;",
    )
    with tags.div(class_="demo-grid"):
        _code_panel(STATE_CODE)
        with tags.div(class_="live-panel"):
            with tags.div(class_="live-header"):
                tags.span(class_="live-dot")
                tags.span("Live demo")
            with tags.div(class_="live-body"):
                with tags.div(class_="state-grid"):
                    StateDisplay()
                    StateControls()
                tags.p("Controls mutates state → Display reloads via SSE", class_="sse-note")


# ── Pages ──────────────────────────────────────────────────────────────────────

@docs_router.page("/docs", head_renderer=head("Introduction", hljs=False))
def docs_intro():
    _docs_page("/docs", _intro_content)


@docs_router.page("/docs/how-it-works", head_renderer=head("How it works", hljs=False))
def docs_how_it_works():
    _docs_page("/docs/how-it-works", _how_it_works_content)


@docs_router.page("/docs/quickstart", head_renderer=head("Quick start", hljs=True))
def docs_quickstart():
    _docs_page("/docs/quickstart", _quickstart_content)


@docs_router.page("/docs/router", head_renderer=head("Router", hljs=True))
def docs_router_page():
    _docs_page("/docs/router", _router_content)


@docs_router.page("/docs/page", head_renderer=head("Page", hljs=True))
def docs_page_route():
    _docs_page("/docs/page", _page_content)


@docs_router.page("/docs/tags", head_renderer=head("Tags", hljs=True))
def docs_tags():
    _docs_page("/docs/tags", _tags_content)


@docs_router.page("/docs/attributes", head_renderer=head("Attributes", hljs=True))
def docs_attributes():
    _docs_page("/docs/attributes", _attributes_content)


@docs_router.page("/docs/components", head_renderer=head("Components", hljs=True))
def docs_components():
    _docs_page("/docs/components", _components_content)


@docs_router.page("/docs/reloading", head_renderer=head("Reloading", hljs=True))
def docs_reloading():
    _docs_page("/docs/reloading", _reloading_content)


@docs_router.page("/docs/indicators", head_renderer=head("Indicators", hljs=True))
def docs_indicators():
    _docs_page("/docs/indicators", _indicators_content)


@docs_router.page("/docs/reload-request", head_renderer=head("ReloadRequest", hljs=True))
def docs_reload_request():
    _docs_page("/docs/reload-request", _reload_request_content)


@docs_router.page("/docs/container", head_renderer=head("Container", hljs=True))
def docs_container():
    _docs_page("/docs/container", _container_content)


@docs_router.page("/docs/state", head_renderer=head("State", hljs=True))
def docs_state():
    _docs_page("/docs/state", _state_content)
