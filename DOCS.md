# LazyFast documentation

## Table of contents

- [How LazyFast works](#how-lazyfast-works)
- [Application router](#application-router)
  - [Multiple routers](#multiple-routers)
- [Page](#page)
  - [Custom scripts and styles](#custom-scripts-and-styles)
- [Tag](#tag)
  - [Nesting](#nesting)
  - [Attributes](#attributes)
    - [Standard HTML attributes](#standard-html-attributes)
    - [LazyFast specific attributes](#lazyfast-specific-attributes)
      - [`allow_unsafe_html`](#allow_unsafe_html)
    - [HTMX](#htmx)
    - [Dataset](#dataset)
  - [Custom tags](#custom-tags)
- [Component](#component)
  - [Define a component](#define-a-component)
    - [View endpoint](#view-endpoint)
    - [Parameters](#parameters)
  - [Reloading](#reloading)
    - [Tag interactivity](#tag-interactivity)
    - [State field changes](#state-field-changes)
    - [Self reloading](#self-reloading)
    - [Indicators](#indicators)
    - [`ReloadRequest`](#reloadrequest)
    - [Container customization](#container-customization)
- [State](#state)
  - [Define state](#define-state)
  - [Load state](#load-state)
  - [Commit state](#commit-state)


# How LazyFast works

LazyFast builds interactive web UIs from Python using FastAPI and HTMX. Here is what happens when a user opens a page:

1. The browser requests the page — FastAPI returns a full HTML document with HTMX and LazyFast's JS included.
2. Each **component** on the page renders as an empty `<div>` with HTMX attributes. HTMX immediately fires a `POST` request back to the server to load the component's content.
3. The server runs the component's `view()` method and returns the rendered HTML fragment. HTMX swaps it into the page — no full reload.
4. When the user interacts (clicks a button, types in an input), HTMX fires another `POST` to re-render only that component, sending all current input values. The component re-runs its `view()` with fresh data.
5. For background-driven updates (e.g. a price feed), a persistent **Server-Sent Events** (SSE) connection tells the browser which component IDs to reload.

This means you write only Python — no JavaScript needed for most use cases.


# Application router

LazyFast is built as a FastAPI `APIRouter` subclass. You attach it to a `FastAPI` app with `include_router`, just like any other router:

```python
from fastapi import FastAPI
from lazyfast import LazyFastRouter

app = FastAPI()
router = LazyFastRouter()

app.include_router(router)
```

That's all the setup you need to get started. Pages and components are then registered on `router`.

## Multiple routers

You can use multiple LazyFast routers to split a large app into independent sections (e.g. public site, admin panel, API). Each router manages its own sessions and state.

LazyFast registers internal endpoints (SSE, component loaders) under a `loader_route_prefix`. When using multiple routers, **each one must have a unique prefix** to avoid route collisions:

```python
from fastapi import FastAPI
from lazyfast import LazyFastRouter

app = FastAPI()

home_router    = LazyFastRouter(loader_route_prefix="/__lf_home__")
account_router = LazyFastRouter(loader_route_prefix="/__lf_account__")
admin_router   = LazyFastRouter(loader_route_prefix="/__lf_admin__")

app.include_router(home_router)
app.include_router(account_router)
app.include_router(admin_router)
```

> ⚠️ Do **not** use FastAPI's `prefix` parameter on a `LazyFastRouter`. The internal SSE and component endpoints use the `loader_route_prefix` as an absolute path, so adding a FastAPI prefix would cause a mismatch and break those endpoints. Use unique `loader_route_prefix` values instead.


# Page

Every LazyFast tag and component must run inside a **page**. A page is a regular FastAPI endpoint decorated with `@router.page(path)`. LazyFast automatically wraps your output in a complete HTML document and injects the required JavaScript. You do not return anything — LazyFast collects all tags and builds the `HTMLResponse` for you.

```python
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
```

`GET /?query=example` returns:

```html
<div>
    <h1>Hello, World!</h1>
    <span>example</span>
</div>
```

The page function supports all FastAPI dependency injection. Components placed inside a page are lazy-loaded automatically:

```python
@router.component()
class MyComponent(Component):
    async def view(self):
        tags.div("My lazy loaded component")

@router.page("/")
def index():
    MyComponent()
```


## Custom scripts and styles

Use the `head_renderer` parameter to inject custom tags (meta, link, script, style) into the `<head>`:

```python
def cdn_libs_and_meta():
    tags.meta(charset="utf-8")
    tags.meta(name="viewport", content_="width=device-width, initial-scale=1")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3/dist/css/bootstrap.min.css"
    )
    tags.script(
        src="https://cdn.jsdelivr.net/npm/bootstrap@5.3/dist/js/bootstrap.bundle.min.js"
    )

@router.page("/", head_renderer=cdn_libs_and_meta)
def index():
    with tags.div(class_="container"):
        tags.span("This page uses Bootstrap")
```


# Tag

Tags are Python wrappers for HTML elements. Each tag corresponds to an HTML element of the same name. You can import them from `lazyfast.tags`:

```python
from lazyfast import tags          # access as tags.div, tags.span, …
from lazyfast.tags import div, p   # or import individually
```


## Nesting

Use `with` to nest tags inside other tags, exactly like HTML structure:

```python
with tags.div(class_="box", id="box"):
    with tags.div(class_="content"):
        tags.h1("Hello, World!")
    with tags.div(class_="control"):
        tags.button("Click me!", id="btn")
```

Produces:

```html
<div class="box" id="box">
    <div class="content">
        <h1>Hello, World!</h1>
    </div>
    <div class="control">
        <button id="btn">Click me!</button>
    </div>
</div>
```

To add plain text inside a tag, pass it as the first positional argument:

```python
tags.p("Hello, world!")
```

> ⚠️ You cannot combine text content and `with` nesting on the same tag:
> ```python
> with tags.div("Some text"):   # raises TypeError
>     tags.span("child")
> ```


## Attributes

### Standard HTML attributes

Almost all standard HTML attributes are supported directly as keyword arguments. A few names end with an underscore because the original name conflicts with a Python built-in or reserved word:

```json
{
    "class_":   "class",
    "dir_":     "dir",
    "async_":   "async",
    "type_":    "type",
    "for_":     "for",
    "content_": "content"
}
```

For example, to set the `type` attribute on an `<input>`:

```python
tags.input(type_="text", name="username")
```


### LazyFast specific attributes

#### `allow_unsafe_html`

By default, text content is HTML-escaped for safety. Set `allow_unsafe_html=True` to render raw HTML inside a tag:

```python
tags.div("<b>Bold text</b>", allow_unsafe_html=True)
```

Renders as:

```html
<div><b>Bold text</b></div>
```

> ⚠️ Only use this with content you fully control. Never pass user-supplied strings with `allow_unsafe_html=True`.


### HTMX

LazyFast uses HTMX internally and covers the most common use cases automatically. For advanced scenarios you can pass an `HTMX` instance directly:

```python
from lazyfast.htmx import HTMX

hx = HTMX(url="/some/endpoint", method="post", trigger="reveal")
tags.div(hx=hx)
```

Renders as:

```html
<div hx-post="/some/endpoint" hx-trigger="reveal"></div>
```


### Dataset

Use the `dataset` dict to set `data-*` attributes:

```python
tags.div(dataset={
    "custom-attribute": "value",
    "another-attribute": "other",
})
```

Renders as:

```html
<div data-custom-attribute="value" data-another-attribute="other"></div>
```


## Custom tags

If a tag you need is missing, subclass `Tag` and add your attributes:

```python
from dataclasses import dataclass
from lazyfast.tags import Tag

@dataclass(slots=True)
class MyCustomTag(Tag):
    my_attribute: str | None = None
```


# Component

A component is an independently re-renderable piece of UI. It is defined as a Python class with a `view()` method and registered on the router with `@router.component()`. Components support lazy loading, interactivity, and automatic reloading — all without writing JavaScript.


## Define a component

```python
@router.component()
class MyComponent(Component):
    async def view(self):
        tags.div("My lazy loaded component")

@router.page("/")
def index():
    MyComponent()
```

When the page loads, the browser receives a placeholder `<div>` with HTMX attributes:

```html
<div
    class="__componentLoader__"
    id="MyComponent"
    hx-post="/__lazyfast__/MyComponent"
    hx-include="#csrf, #MyComponent"
    hx-trigger="load, MyComponent"
></div>
```

HTMX immediately fires a POST to load the component. After the response arrives:

```html
<div
    class="__componentLoader__"
    id="MyComponent"
    hx-post="/__lazyfast__/MyComponent"
    hx-include="#csrf, #MyComponent"
    hx-trigger="load, MyComponent"
>
    <div>My lazy loaded component</div>
</div>
```


### View endpoint

`view()` is a full FastAPI endpoint and supports dependency injection:

```python
async def my_dependency() -> str:
    return "injected value"

@router.component()
class MyComponent(Component):
    async def view(self, dep: str = Depends(my_dependency)):
        tags.div(f"Dependency result: {dep}")
```


### Parameters

Component parameters are fields that customize the component instance. They are passed when placing the component in a page:

```python
@router.component()
class MyComponent(Component):
    edit: bool = False

    async def view(self):
        if self.edit:
            tags.div("Edit mode")
        else:
            tags.div("Read mode")

@router.page("/")
def index():
    MyComponent(edit=True)
```


## Reloading

Component reloading is the mechanism that makes UIs interactive. When a reload is triggered, the browser sends a POST to the component's `view` endpoint, which re-runs and returns fresh HTML. All current input values are included in the request automatically.

Reloads can be triggered by: tag events, state field changes, or the component itself.


### Tag interactivity

The following tags trigger a component reload automatically when the user interacts with them:

| Tag                       | Default event |
| ------------------------- | ------------- |
| `input`                   | `change`      |
| `button`                  | `click`       |
| `select`                  | `change`      |
| `input(type_="radio")`    | `click`       |
| `input(type_="checkbox")` | `change`      |
| `textarea`                | `input`       |

To override or add events, use the `reload_on` attribute with a list of event names (without the `on` prefix):

```python
tags.input(type_="text", name="q", reload_on=["change", "keydown"])
```

#### `trigger`

Each interactive tag exposes a `trigger` property. It returns the JavaScript event name that caused the last reload, or `None` if the tag was not the trigger. The tag must have an `id` to use `trigger`:

```python
@router.component()
class MyComponent(Component):
    async def view(self):
        inp = tags.input(type_="text", id="search", name="q")
        if inp.trigger:
            tags.div(f"Search triggered by: {inp.trigger}")

        btn = tags.button("Submit", id="submit_btn")
        if btn.trigger:
            tags.div("Button was clicked")
```

To disable the automatic reload for inputs inside a form (except buttons), wrap them in a `form` tag:

```python
@router.component()
class MyComponent(Component):
    async def view(self):
        with tags.form():
            tags.input(type_="text", name="q")  # does NOT reload on change

            btn = tags.button("Search", id="search_btn")
            if btn.trigger:
                tags.div("Searching…")
```


### State field changes

A component can subscribe to changes in a state field. Whenever that field is updated and committed, the component reloads automatically via SSE — no browser polling required.

To use this, the component must have an explicit `id`:

```python
@router.component(id="my_component", reload_on=[State.my_field])
class MyComponent(Component):
    async def view(self, state: State = Depends(State)):
        tags.span(str(state.my_field))
```

See the [State](#state) section for details on defining and updating state.


### Self reloading

A component can push a reload to itself via SSE. This is useful for live-updating displays like clocks, prices, or progress bars:

```python
import asyncio
import random

@router.component(id="live_number")
class LiveNumber(Component):
    async def view(self):
        tags.span(str(random.randint(0, 100)))
        await asyncio.sleep(1)
        await self.reload()
```

The component re-renders every second. You must specify an `id` for the component decorator when using `self.reload()`.


### Indicators

While a component waits for a server response, you can show the user a loading state using two approaches — they can also be combined.

**`is_indicator=True`** — hides the tag by default, shows it during reload:

```python
@router.component()
class MyComponent(Component):
    async def view(self):
        tags.button("Run")
        tags.span("Loading…", is_indicator=True)
```

**`data-htmx-indicator-class`** — adds a CSS class to a tag during reload without hiding it:

```python
@router.component()
class MyComponent(Component):
    async def view(self):
        tags.button("Run", dataset={"htmx-indicator-class": "is-loading"})
        tags.span("Loading…", is_indicator=True)
```

In this example the button gets the `is-loading` class added while the component is reloading, and the span is shown.


### `ReloadRequest`

Every component reload sends a `ReloadRequest` that carries metadata about what triggered the reload. Injecting it via `Depends` lets you branch logic without waiting for tags to render:

```python
from lazyfast import ReloadRequest

@router.component()
class MyComponent(Component):
    async def view(self, req: ReloadRequest = Depends(ReloadRequest)):
        if req.trigger_id == "action_btn":
            tags.span("Button was clicked")

        tags.button("Action", id="action_btn")
```

`ReloadRequest` properties:

| Property        | Type            | Description                                      |
| --------------- | --------------- | ------------------------------------------------ |
| `method`        | `str`           | `"GET"` or `"POST"`                              |
| `trigger_id`    | `str \| None`   | `id` of the tag that triggered the reload        |
| `trigger_event` | `str \| None`   | JavaScript event name (e.g. `"click"`)           |
| `inputs`        | `dict`          | Current values of all inputs in the component    |
| `session_id`    | `str`           | Unique ID for the current user session           |

> Using `ReloadRequest` separates display logic from business logic, which is helpful in large components.


### Container customization

The `@router.component()` decorator accepts optional styling and preload arguments:

```python
@router.component(class_="my-class", preload_renderer=lambda: tags.div("Loading…"))
class MyComponent(Component):
    async def view(self):
        tags.div("My component")
```

Before the component loads:

```html
<div class="my-class __componentLoader__" hx-…>
    <div>Loading…</div>
</div>
```

After the component loads:

```html
<div class="my-class __componentLoader__" hx-…>
    <div>My component</div>
</div>
```

The `swapping_method` parameter controls how new content replaces old content (default `"replace"`):

```python
@router.component(swapping_method="append")
class MyComponent(Component):
    async def view(self):
        tags.li("New item")
```


# State

State lets multiple components share and react to the same data. Define a state model by subclassing `BaseState`. Each router can have one state schema, and each user session has its own isolated state instance.

Behind the scenes, state updates travel from the server to the browser via SSE, triggering only the components that subscribed to changed fields.


## Define state

```python
from lazyfast import LazyFastRouter, BaseState

class AppState(BaseState):
    count: int = 0
    message: str = ""

router = LazyFastRouter(state_schema=AppState)
```

Fields can be any type that is serializable (int, str, list, Pydantic model, etc.).


## Load state

Inject the current state into any `view()`, `page()`, or FastAPI endpoint using `Depends`:

```python
from fastapi import Depends
from lazyfast import Component, tags

@router.component()
class Counter(Component):
    async def view(self, state: AppState = Depends(AppState)):
        tags.span(f"Count: {state.count}")
```

```python
@router.page("/")
async def index(state: AppState = Depends(AppState)):
    tags.h1(f"Welcome — current count: {state.count}")
```

The state is loaded from the current session as a snapshot. Changes made to the local `state` object are not visible to other requests until you commit.


## Commit state

To persist changes and notify subscribed components, use the `async with` context manager:

```python
@router.component()
class Counter(Component):
    async def view(self, state: AppState = Depends(AppState)):
        tags.span(f"Count: {state.count}")

        btn = tags.button("Increment", id="inc_btn")
        if btn.trigger:
            async with state:
                state.count += 1
```

The `async with` block:
1. Acquires an exclusive lock on the state (preventing concurrent modifications).
2. Refreshes the local snapshot from the session.
3. On success: persists changes and triggers reloads for subscribed components.
4. On exception: releases the lock **without** saving partial changes.

> ℹ️ **Transaction isolation**
> The state commit system uses pessimistic locking with serializable isolation. When you enter `async with state`, the state is locked to your session until the block exits — other concurrent requests for the same session will wait. This prevents race conditions in multi-component interactions.

To subscribe a component to state field changes, use `reload_on` with a list of state fields and specify an `id` for the component:

```python
@router.component(id="counter_display", reload_on=[AppState.count])
class CounterDisplay(Component):
    async def view(self, state: AppState = Depends(AppState)):
        tags.span(f"Count: {state.count}")

@router.component(id="counter_controls")
class CounterControls(Component):
    async def view(self, state: AppState = Depends(AppState)):
        btn = tags.button("Increment", id="inc_btn")
        if btn.trigger:
            async with state:
                state.count += 1
```

When the button is clicked, `count` is incremented and committed. The SSE connection notifies the browser to reload `counter_display` automatically.
