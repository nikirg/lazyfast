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
  - [Caching](#caching)
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
- [Production](#production)


# Application router
LazyFast is very tightly integrated with FastAPI. LazyFast application is a router inherited from `fastapi.APIRouter`. This means that LazyFast can be integrated into an existing FastAPI application, add a URL `prefix`, configure `dependencies` at the router level, and so on. It is implied that logic can be distributed across several LazyFast Routers at once. They isolate the session and state manager within themselves.
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
Every LazyFast tag and component works only in the context of a page. You can define your page with `@router.page` decorator. Page decorator creates endpoint which returns HTML response LazyFast javascript dependencies. Decorated function works like regular FastAPI endpoint, support all dependency injection features, the only exception is, that you don't need to specify return value. LazyFast build and return final `HTMLResponse` impicitly. Also page inject hidden `input` tag with `csrf` token.
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
This example will add bootstrap css and js to the page head. 
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
Library provides almost all standard HTML attributes and lazyfast specific attributes for component's interactivity. Under the hood, LazyFast uses the `dataclasses` to implement tags logic and attributes.

### Standart html attributes
Almost all tag's attributes duplicates standart HTML attributes, but several of them ends with underscore, because in their original form they coincid with python reserved words or built-in methods.
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
Function `reloadComponent` is library internal javascript function, based on HTMX, that reloads a component and send all input values to the server. There is no necessity use this function directly in your code. We advise to use `reload_on` parameter with a list of events.

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
This `span` tag is not visible when the component is not in reloading process. Reloading process is the time between `reloadComponent` function trigger and the server response.

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
LazyFast library uses the `htmx` library to implement client-server interaction. It presented by the `HTMX` class, which implements limited HTMX features. `HTMX` class is used in internal library logic, and you don't need to use it in the most common use cases. But you can use it in custom scenarios by setting `hx` tag parameter with the `HTMX` instance.
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
LazyFast library allows you to nest tags and components in the same way as HTML. This is being implemented using python `with` operator
```python
# field div inside box div
with tags.div(class_="box", id="box"):
    with tags.div(class_="field"):
```
Nesting don't have any limitation on the nesting level. You can use any number of nested tags and components in the same way as HTML.
In case when you want nest just a plain text, use `content` tag parameter, first optional positional argument. 
>   
> ⚠️ You can't use `with` and `content` nesting at the same time
> ```python
> with tags.div("Hello world", class_="box", id="box"):
>     tags.span()
> ```
> This code raises an error
> 

## Caching
Coming soon...

## Custom tags
If you want to use your own tags, or LazyFast library doesn't support existed HTML tags, you can create it by inheriting from the `Tag` class and decorate it with `@dataclass(slots=True)` decorator:
```python
from dataclasses import dataclass
from lazyfast.tags import Tag

@dataclass(slots=True)
class MyCustomTag(Tag):
    my_attribute: str | None = None
```

# Component
A component is a class that allows you to build complex nested web interfaces with interactivity and lazy loading. Components help reuse code and distribute it into logical blocks.
Components can be nested in pages or in other components.

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
From the HTML point of view, creating a component object is creating a `div` tag with special HTMX settings.

### View endpoint
View endpoint register by component decorator and is called from cliet side.
This endpoint completely coresponds to the Fastapi endpoint, with all dependency injection features and async support.
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
Component reloadind is the key feature of component interacivity. LazyLoad insipred by **Streamlit**, which reloads (rerun in Streamlit) page after interaction with inputs, buttons and so on. From Streamlit **1.33.0** you can use fragments - oportunity to rerun only party of page. LazyFast components interactivity is every similar to fragments, but more flexible and with multiple nesting support. 
Reload is trgiggered by many source of events: tags interactivity, state fields changes and self reloading. Reloading is a `post` request from client to the component's view endpoint at the server and receiving the result of its rendering. Each new reload sends the values ​​of various fields entered by the client to the server and makes it possible to dynamically change the component's appearance on the client.

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

To determine the source of the reload, each interactive tag has a `trigger` property, which is either `None` if it was not the source, or contains the text value of the javascript event:
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
The component can be subscribed to changes in state fields, if the specified fields have updated their values, the component is reloaded. This happens through the `SSE` without the need to manually refresh the browser page.
```python
@router.component(id="MyComponent", reload_in=[State.my_field])
class MyComponent(Component):
    def view(self, state: State = Depends(State.load)):
        tags.span(state.my_field)
            
```
For state changes listening you nedd to specify `id` property of the component decorator.

### Self reloading
The component can reload itself, this also happens through `SSE`, without the need to reload the page:
```python
@router.component(id="MyComponent")
class MyComponent(Component):
    async def view(self):
        random_number = random.randint(0, 100)
        tags.span(random_number)
        await asyncio.sleep(1)
        await self.reload()
            
```
This example reloads the component every second, which displays a random number. You also need to specify `id` property of the component decorator. It means that you set `id` of `div` component container on HTML page.

### Indicators
After the component has sent a reload request to the server, but has not yet received a response, it is necessary to somehow show the user the waiting state. For this, you can use any tag with the `indicator` attribute. Such a tag automatically becomes hidden and appears only during the reload process. If you need to change the appearance of tags without hiding them, you can specify the reserved field `htmx-indicator-class` inside dataset attribute and specify the class that will be assigned to the tag during the reload process.
```python
@router.component()
class MyComponent(Component):
    def view(self):
        dataset = {"htmx-indicator-class": "is-loading"}
        tags.button("Run reloading", dataset=dataset) 
        tags.span("Loading...", is_indicator=True)
```
This example hide `span` by default and show after button click. And add `is-loading` class to the button.

### `ReloadRequest`
Previously, we described ways to hadnle the reload via the property trigger, but this approach requires us to wait for the entire current tag structure to render. However, we may have a scenario in which we must completely rebuild the component based on incoming data from the user. LazyFast has a `ReloadRequest` object for this.
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


### Container customization
The component register decorator allows you to change the customize `div` container class and pass `preload_renderer` callable to specify the function that will be called before the component is rendered. This can be useful when you need to render for example skeletons.
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
State management allows different components to interact with each other through a convenient single interface. State is a pydantic base class that can have an unlimited number of fields, the update of which can be subscribed to by components. Within the framework of `LazyFastRouter` there can be only one model of state. The state is stored in the user session, isolated from other sessions. Under the hood, the state interacts with components through an asynchronous queue and `SSE`.

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
You alson can use `State.load` within `@router.page` decorator and other FastAPI endpoints:
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
In order for the field update to trigger a reload of all dependent components, it is necessary to use the commit mechanism. We can use this mechanism in several ways:
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
        await state.close()

        # or
        # directly `open` and `commit` with try/finally
        try:
            state.open()
            state.my_field = 1
        finally:
            await state.close()
...
```
After this three ways of state commit, the component will be reloaded with the new state value.

## Session API
Coming soon...

# Production
Coming soon...
