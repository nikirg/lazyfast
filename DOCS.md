# LazyFast documentation
## Table of contents:

- [LazyFast documentation](#lazyfast-documentation)
  - [Table of contents:](#table-of-contents)
- [Application router](#application-router)
- [Page](#page)
  - [Custom scripts and styles](#custom-scripts-and-styles)
- [Tag](#tag)
  - [Attributes](#attributes)
    - [Standart html attributes](#standart-html-attributes)
    - [LazyFast specific attributes](#lazyfast-specific-attributes)
      - [`reload_on`](#reload_on)
      - [`is_indicator`](#is_indicator)
      - [`allow_unsafe_html`](#allow_unsafe_html)
    - [HTMX](#htmx)
    - [Dataset](#dataset)
    - [Dynamic editing](#dynamic-editing)
  - [Nesting](#nesting)
  - [Custom tags](#custom-tags)
- [Component](#component)
  - [Define a component](#define-a-component)
    - [View endpoint](#view-endpoint)
    - [Parameters](#parameters)
  - [Reloading](#reloading)
    - [Tags interactivity](#tags-interactivity)
    - [State fields changes](#state-fields-changes)
    - [Self reloading](#self-reloading)
    - [Indicators](#indicators)
    - [`ReloadRequest`](#reloadrequest)
    - [Container customization](#container-customization)
- [State](#state)
  - [Define state](#define-state)
  - [Load state](#load-state)
  - [Commit state](#commit-state)
  - [Session API](#session-api)


# Application router
LazyFast is deeply integrated with FastAPI. A LazyFast application is built as a router that inherits from `fastapi.APIRouter`. This allows you to easily integrate LazyFast into an existing FastAPI application, add a URL prefix, and configure dependencies at the router level, among other features. You can also distribute logic across multiple LazyFast routers, with each router managing its own session and state independently.
```python
from fastapi import FastAPI
from lazyfast import LazyFastRouter

app = FastAPI()

root_router = LazyFastRouter(prefix="/")
login_router = LazyFastRouter(prefix="/login")
project_router = LazyFastRouter(prefix="/project")

app.include_router(root_router)
app.include_router(login_router)
app.include_router(project_router)
```

# Page
Every LazyFast tag and component operates within the context of a page. You can define a page using the `@router.page` decorator. This decorator creates an endpoint that returns an HTML response along with LazyFast's JavaScript dependencies. The decorated function behaves like a regular FastAPI endpoint and supports all dependency injection features. However, you don’t need to specify a return value — LazyFast automatically builds and returns the final `HTMLResponse`. Additionally, the page injects a hidden `input` tag containing a csrf token.
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
This code means, that HTTP `GET /?query=example` request will return:
```html
<div>
    <h1>Hello, World!</h1>
    <span>example</span>
</div>
```
LazyFast key feature component interactivity and lazy loading work only within page:
```python
from fastapi import FastAPI
from lazyfast import LazyFastRouter, Component, tags

router = LazyFastRouter()

@router.component()
class MyComponent(Component):    
    def view(self):
        tags.div("My lazy loaded component")

@router.page("/")
def index():
    MyComponent()

app = FastAPI()
app.include_router(router)
```

## Custom scripts and styles
To pass your custom javascript or css in the page, you can use `head_renderer` parameter in `@router.page` decorator. This argument accepts function, wich will be called inside `head` tag.
```python
...
def cdn_libs_and_meta():
    tags.meta(charset="utf-8")
    tags.meta(name="viewport", content="width=device-width, initial-scale=1")
    tags.link(
        rel="stylesheet", 
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
    )
    tags.script(
        src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"
    )

@router.page("/", head_renderer=cdn_libs_and_meta)
def index():
    with tags.div(class_="container"):
        tags.span(f"This page is use bootstrap v5.1.3")
...
```
This example will add `bootstrap` css and js to the page head. 
You also can `meta` tag inside the `head_renderer` function.

# Tag
In LazyFast tag is a simple wrapper for HTML tags:
```python
from lazyfast import tags

with tags.div(class_="box", id="box"):
    with tags.div(class_="content"):
        tags.h1("Hello, World!")
    with tags.div(class_="control"):
        tags.button("Click me!", id="btn")
```
The code above is equivalent to:
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
You also can import tags separately:
```python
from lazyfast.tags import div, span, h1
```

## Attributes
The library supports nearly all standard HTML attributes, along with LazyFast-specific attributes for enhancing component interactivity. Under the hood, LazyFast uses Python `dataclasses` to manage the logic behind tags and attributes.

### Standart html attributes
Almost all tag attributes correspond to standard HTML attributes. However, some end with an underscore because their original form conflicts with Python reserved words or built-in methods.
This is a map between original and lazyfast attributes:
```json
{
    "class_": "class",
    "dir_": "dir",
    "async_": "async",
    "type_": "type",
    "for_": "for",
    "content_": "content",
}
```

### LazyFast specific attributes
Specific attributes are used in the many ways to make componentns interactive and responsive.

#### `reload_on`
In order for a component to be reloaded by an HTML event in a tag, you can set the `reload_on` tag parameter with a list of events:
```python
tags.input(type_="text", reload_on=["change", "keydown"])
```
It is equivalent to:
```html
<div
    type="text" 
    onchange="reloadComponent(this, event)" 
    onkeydown="reloadComponent(this, event)"
></div>
```
The `reloadComponent` function is an internal JavaScript function in the library, built on HTMX. It reloads a component and sends all input values to the server. You don't need to use this function directly in your code. Instead, we recommend using the `reload_on` parameter with a list of events to trigger component reloads.

#### `is_indicator`
This attribute is used to show or hide a tag when component is in reloading process. Is is equivalent to `htmx-indicator` class. The most frequent use case is to show a loader or spinner during reloading.
```python
# Button tag already has onclick reloading by default,
# but we set this attribute explicitly to show the mechanism
tags.button("Run reloading", reload_on=["click"]) 
tags.span("Loading...", is_indicator=True)
```
Direct way to set the `htmx-indicator` class:
```python
tags.button("Run reloading", reload_on=["click"]) 
tags.span("Loading...", class_="htmx-indicator")
```
The `span` tag is hidden when the component is not in the process of reloading. The reloading process occurs between the trigger of the `reloadComponent` function and the server's response.

#### `allow_unsafe_html`
For the purpose of security, we use `allow_unsafe_html` to allow use of unsafe HTML in the component. This attribute is `False` by default. Use case example:
```python
tags.div("Hello, <b>World!</b>", allow_unsafe_html=True)
``` 
is equivalent to:
```html
<div>Hello, <b>World!</b></div>
```

### HTMX
The LazyFast library uses the `htmx` library to handle client-server interactions, represented by the HTMX class, which implements a limited set of htmx features. In most common use cases, you won't need to interact directly with the HTMX class, as it is used internally by the library. However, for custom scenarios, you can manually use it by setting the `hx` tag parameter with an instance of HTMX.
```python
hx = HTMX(url="/some/endpoint", method="post", trigger="reveal")
tags.div(hx=hx)
```
Is equivalent to:
```html
<div hx-post="/some/endpoint" hx-trigger="reveal"></div>
```
### Dataset
LaztFast implements `data-*` attributes in tags via `dataset` attribute with dictionary type:
```python
dataset = {
    "custom-attribute": "value",
    "another-custom-attribute": "another-value",
}
tags.div(dataset=dataset)
```
Is equivalent to:
```html
<div data-custom-attribute="value" data-another-custom-attribute="another-value"></div>
```

### Dynamic editing
Coming soon...

## Nesting
The LazyFast library lets you nest tags and components just like you would in HTML. This is achieved using Python's `with` statement.
```python
# field div inside box div
with tags.div(class_="box", id="box"):
    with tags.div(class_="field"):
```
There are no limitations on the nesting level — you can nest as many tags and components as you like, similar to HTML. 
If you want to nest plain text, use the `content` tag parameter, which is the first optional positional argument.
>   
> ⚠️ You can't use `with` and `content` nesting at the same time
> ```python
> with tags.div("Hello world", class_="box", id="box"):
>     tags.span()
> ```
> This code raises an error
> 

## Custom tags
If you want to use custom tags or if the LazyFast library doesn't support certain existing HTML tags, you can create your own by inheriting from the `Tag` Tag class and using the `@dataclass(slots=True)` decorator:
```python
from dataclasses import dataclass
from lazyfast.tags import Tag

@dataclass(slots=True)
class MyCustomTag(Tag):
    my_attribute: str | None = None
```

# Component
A component is a class that helps you create complex, interactive web interfaces with lazy loading. It enables code reuse by organizing your interface into logical blocks. Components can be nested within pages or even inside other components, allowing for flexible and scalable design.

## Define a component
Creating a component consists of declaring a class inherited from `Component` and registering the component in the router with the appropriate decorator.
```python
from fastapi import FastAPI
from lazyfast import LazyFastRouter, Component, tags

router = LazyFastRouter()

@router.component()
class MyComponent(Component):
    def view(self):
        tags.div("My lazy loaded component")

@router.page("/")
def index():
    MyComponent()

app = FastAPI()
app.include_router(router)
```
When, you go to the `/` page, you will see the following:
```html
<div 
    class="__componentLoader__" 
    id="MyComponent" 
    hx-post="/" 
    hx-include="#csrf, #MyComponent" 
    trigger="load, MyComponent"
></div>
```
And after the component is loaded, you will see:
```html
<div
    class="__componentLoader__"
    id="MyComponent"
    hx-post="/"
    hx-include="#csrf, #MyComponent"
    hx-trigger="load, MyComponent"
>
    <div>My lazy loaded component</div>
</div>
```
From an HTML perspective, creating a component involves generating a `div` tag with specific HTMX attributes.

### View endpoint
The `view` endpoint, registered using the component decorator, is called from the client side. This endpoint fully corresponds to a FastAPI endpoint, supporting all dependency injection features and asynchronous functionality.
```python
...
async def my_dependency() -> str:
    return "My dependency"

@router.component()
class MyComponent(Component):
    async def view(self, dep_result: str = Depends(my_dependency)):
        tags.div(f"My lazy loaded component and dependency result: {dep_result}")
...
```

### Parameters
Paramters are pydantic model fields, which can be used to parameterize view logic or local state of the component.
```python
...
@router.component()
class MyComponent(Component):
    edit: bool = False

    def view(self):
        if self.edit:
            tags.div("Edit mode")
        else:
            tags.div("Read mode")
        
@router.page("/")
def index():
    MyComponent(edit=True)
...
```

## Reloading
Component reloading is a key feature for enabling interactive components in LazyFast. The concept is inspired by Streamlit, where the entire page is reloaded (or "rerun") after interactions with inputs, buttons, and other elements. Starting from Streamlit 1.33.0, fragments allow for partial page reruns. LazyFast’s component interactivity is similar to Streamlit's fragments but offers more flexibility with support for multiple nested components.

Reloading is triggered by various sources, such as tag interactions, changes in state fields, and self-reloading mechanisms. This process involves the client sending a `POST` request to the component’s view endpoint on the server, receiving the newly rendered component in response. Each reload sends the current field values from the client to the server, enabling dynamic changes to the component’s appearance based on user input.

### Tags interactivity
In LazyFast, the following tags are endowed with interactivity:
| Tag        | Default Event (on*) |
| ---------- | ------------------- |
| `input`    | change              |
| `button`   | click               |
| `select`   | change              |
| `radio`    | click               |
| `checkbox` | change              |
| `textarea` | input               |

Each interactive tag has a `trigger` property that indicates whether it caused the reload. If the tag was not the source, trigger will be `None`. If it was the source, trigger will contain the name of the JavaScript event that triggered the reload:
```python
...
@router.component()
class MyComponent(Component):
    def view(self):
        with tags.div():
            if event := tags.input(type="text").trigger:
                tags.div(f"Text was changed, event: {event}")

            btn = tags.button(type="button")
            if trigger := btn.trigger:
                tags.div(f"Button was clicked, event: {trigger}")
...
```

You can prevent reloading by these tags by wrapping them with `form` tag:
```python
@router.component()
class MyComponent(Component):
    def view(self):
        with tags.form():
            tags.input(type="text")
            
            btn = tags.button(type="button")
            if trigger := btn.trigger:
                tags.div(f"Button was clicked, event: {trigger}")
``` 
Form prevents all reloads except `button` tags.

### State fields changes
The component can subscribe to changes in specific state fields. When any of these fields are updated, the component automatically reloads. This is done via Server-Sent Events (SSE), eliminating the need for manual browser refreshes.
```python
@router.component(id="MyComponent", reload_in=[State.my_field])
class MyComponent(Component):
    def view(self, state: State = Depends(State.load)):
        tags.span(state.my_field)
            
```
To enable state change listening, you need to specify the `id` property in the component decorator.

### Self reloading
The component can automatically reload itself via SSE (Server-Sent Events) without requiring a full page reload:
```python
@router.component(id="MyComponent")
class MyComponent(Component):
    async def view(self):
        random_number = random.randint(0, 100)
        tags.span(random_number)
        await asyncio.sleep(1)
        await self.reload()
            
```
This example reloads the component every second, displaying a random number. You must also specify the `id` property in the component decorator. This sets the `id` of the `div` element that contains the component on the HTML page.

### Indicators
When a component sends a reload request to the server but hasn't yet received a response, it's important to show the user that the system is processing. To indicate this waiting state, you can use any tag with the `is_indicator` attribute. This tag will remain hidden until the reload process begins, at which point it becomes visible.

If you prefer not to hide the tag but want to modify its appearance during the reload, you can use the `htmx-indicator-class` field inside the tag's dataset attribute. This allows you to assign a CSS class to the tag during the reload process, changing its appearance without hiding it.
```python
@router.component()
class MyComponent(Component):
    def view(self):
        dataset = {"htmx-indicator-class": "is-loading"}
        tags.button("Run reloading", dataset=dataset) 
        tags.span("Loading...", is_indicator=True)
```
This example hides the `span` element by default and shows it after the `button` is clicked. Additionally, it adds the `is-loading` class to the `button` without hiding it.

### `ReloadRequest`
In the past, we discussed handling reloads using the `trigger` property, which requires waiting for the current tag structure to finish rendering. However, there are situations where we need to rebuild the entire component based on new data from the user. For these cases, LazyFast provides a `ReloadRequest` object to facilitate this.
```python
@router.component()
class MyComponent(Component):
    def view(self, reload_request: ReloadRequest = Depends(ReloadRequest)):
        if reload_request.trigger_id == "my-id":
            tags.span("Reloaded by my-id")
        tags.button("Run reloading", id="my-id") 
```
`ReloadRequest` object has following properties:
- `method`: `GET` or `POST`
- `trigger_id`: `None` or trigger tag id
- `trigger_event`: `None` or trigger javascript event (e.g. `click`, `change`, or `input`)
- `data`: `None` or request form data (values from all input tags within the component)
- `session_id`: current unique session id 

> Using a `ReloadRequest` allows you to separate the display from the logic, which is especially important in the context of large components.

### Container customization
The component register decorator lets you customize the `div` container class and pass a `preload_renderer` function. This function will be called before the component is rendered, which is helpful for scenarios like rendering skeletons.
```python
@router.component(class_"my-class", preload_renderer=lambda: tags.div("Loading..."))
class MyComponent(Component):
    def view(self):
        tags.div("My component")
```
It equivalent to:
```html
<div class="my-class __componentLoader__" hx-...>
    <div>Loading...</div>
</div>
```
And after the component is rendered:
```html
<div class="my-class __componentLoaded__" hx-...>
    <div>My component</div>
</div>
```
 
# State
State management in LazyFast enables components to interact with each other through a unified interface. The `State` class, which is based on Pydantic, can have any number of fields. Components can subscribe to updates to these fields. Within `LazyFastRouter`, only one state model can be used, and this state is stored in the user's session, ensuring isolation from other user sessions. Behind the scenes, the state interacts with components using an asynchronous queue and Server-Sent Events (SSE).

## Define state
To define state model you need to inherit `BaseState` class:
```python
from lazyfast import LazyFastRouter, BaseState

class State(BaseState):
    my_field: int = 0

router = LazyFastRouter(state_schema=State)
```
## Load state
To work with the state you can use dependency `State.load`:
```python
...
@router.component()
class MyComponent(Component):
    async def view(self, state: State = Depends(State.load)):
        tags.span(state.my_field)
...
```
The component will be rendered with the current state value.
You also can use `State.load` within `@router.page` decorator and other FastAPI endpoints:
```python
...
@router.page()
async def index(state: State = Depends(State.load)):
    tags.span(state.my_field)

@app.get("/")
async def root(state: State = Depends(State.load)):
    return {"message": state.my_field}
...
```

## Commit state
To ensure that updating a field triggers the reload of all dependent components, the commit mechanism must be used. This mechanism can be applied in several ways:
```python
...
@router.component()
class MyComponent(Component):
    async def view(self, state: State = Depends(State.load)):
        tags.span(state.my_field)

        # `with` operator
        async with state:
            state.my_field = 1

        # or
        # directly `open` and `commit`
        state.open()
        state.my_field = 1
        await state.commit()

        # or
        # directly `open` and `commit` with try/finally
        try:
            state.open()
            state.my_field = 1
        finally:
            await state.commit()
...
```
After committing the state using any of the three methods, the component will reload with the updated state value.
>   
> ⚠️ LazyFast currently lacks a concurrent commit system, so simultaneous state updates from multiple parts of the code within a session (i.e., within a single client) at high frequency may lead to unpredictable behavior. I'm actively working on addressing this issue.

## Session API
Coming soon...

