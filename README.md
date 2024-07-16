# LazyFast

LazyFast is a lightweight Python library designed for building modern web interfaces using a component-based approach. It enables writing page logic on the server side in Python, integrating seamlessly with FastAPI. With LazyFast, interactive elements like inputs, buttons, and selects trigger component reloads that occur on the server, updating the component's state dynamically.

## Key Features

1. **Component-Based Server Rendering**: Build web interfaces using lazy loaded components that encapsulate logic, state, and presentation. 
2. **Server-Side Logic**: Handle interactions and state management on the server, reducing client-side complexity.
3. **FastAPI Integration**: Each component or page is a FastAPI endpoint, allowing for dependency injection and other FastAPI features.
4. **Lightweight**: The only dependencies are FastAPI for Python and HTMX for JavaScript, which can be included via CDN.
5. **State Management**: Utilize a state manager that can trigger component reloads, ensuring a reactive user experience.

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


## License

LazyFast is licensed under the [MIT License](https://github.com/nikirg/lazyfast/blob/main/LICENSE).