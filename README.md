<p align="center">
  <img src="https://raw.githubusercontent.com/nikirg/lazyfast/refs/heads/main/img/logo.png" alt="LazyFast">
</p>
<p align="center">
  <img src="img/title.png" alt="LazyFast">
</p>
<p align="center">
  <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/lazyfast">
  <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/lazyfast">
  <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/lazyfast">
</p>

**LazyFast** is a lightweight Python library for building modern, component-based web interfaces using FastAPI. It handles server-side logic in Python, with interactive elements like inputs and buttons triggering server-side component reloads for dynamic state updates.

**Ideal for Python developers who:**
- Have basic HTML and CSS knowledge and want to build web interfaces without learning complex frontend frameworks like React, Angular, or Vue.

**Suitable for projects that:**
- Have low to medium traffic and can benefit from server-side rendering to offload work from the client's machine. *(Note: High traffic may increase server costs due to backend load.)*
- Require quick prototyping and demos without involving frontend developers. LazyFast offers more flexibility than tools like Streamlit, which can be limiting and produce similar-looking applications.

**Key Features**

1. **Component-Based Server Rendering**
   - Build interfaces with lazy-loaded components that encapsulate logic, state, and presentation.
2. **Server-Side Logic**
   - Manage interactions and state on the server, reducing client-side complexity.
3. **FastAPI Integration**
   - Components and pages are FastAPI endpoints, supporting dependency injection and other features.
4. **Lightweight**
   - Dependencies: FastAPI for Python and HTMX for JavaScript (included via CDN).
5. **State Management**
   - Use a state manager to trigger component reloads for a reactive user experience.

## Installation

To install LazyFast, use pip:

```bash
pip install lazyfast
```
or
```bash
poetry add lazyfast
```

## Quick Start

Here's an example application to demonstrate how LazyFast works:

```python
from fastapi import FastAPI, Request
from lazyfast import LazyFastRouter, Component, tags


# LazyFastRouter inherits from FastAPI's APIRouter
router = LazyFastRouter()

# Define a lazy-loaded HTML component powered by HTMX
@router.component()
class MyComponent(Component):
    title: str

    async def view(self, request: Request) -> None:
        tags.h1(self.title, class_="my-class")

        with tags.div(style="border: 1px solid black"):
            tags.span(request.headers)

# Initialize the page dependencies for component rendering
# The page endpoint is also a FastAPI endpoint
@router.page("/{name}")
def root(name: str):
    with tags.div(class_="container mt-6"):
        MyComponent(title=f"Hello, World from {name}")

# Embed the router in a FastAPI app
app = FastAPI()
app.include_router(router)
```
If you use `uvicorn` instead as a server and want to reload on changes, use the following command:
```bash
uvicorn app:app --reload --timeout-graceful-shutdown 1
```

## Documentation
Documentation can be found [here](https://github.com/nikirg/lazyfast/blob/main/DOCS.md).

## Examples
You can find examples in [examples](https://github.com/nikirg/lazyfast/tree/main/examples).

## License

LazyFast is licensed under the [MIT License](https://github.com/nikirg/lazyfast/blob/main/LICENSE).
