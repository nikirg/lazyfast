# Renderable

Renderable is a lightweight Python library designed for building modern web interfaces using a component-based approach. It enables writing page logic on the server side in Python, integrating seamlessly with FastAPI. With Renderable, interactive elements like inputs, buttons, and selects trigger component reloads that occur on the server, updating the component's state dynamically.

## Key Features

1. **Component-Based Approach**: Build web interfaces using lazy loaded components that encapsulate logic, state, and presentation. 
2. **Server-Side Logic**: Handle interactions and state management on the server, reducing client-side complexity.
3. **FastAPI Integration**: Each component or page is a FastAPI endpoint, allowing for dependency injection and other FastAPI features.
4. **Lightweight**: The only dependencies are FastAPI for Python and HTMX for JavaScript, which can be included via CDN.
5. **State Management**: Utilize a state manager that can trigger component reloads, ensuring a reactive user experience.

## Installation

To install Renderable, use pip:

```bash
pip install renderable
```

## Quick Start

Here's an example application to demonstrate how Renderable works:

```python
from fastapi import FastAPI
from renderable import RenderableRouter, Component, tags

# Renderable router is inherited from FastAPI APIRouter
router = RenderableRouter()

# Renderable component is a lazy loaded html part, powered by HTMX
@router.component()
class MyComponent(Component):
    value: str

    # We can define html rendering logic by overriding the view method
    # View method is FastAPI endpoint, which supports dependency injection
    async def view(self, request: Request) -> None:
        # We can use familiar html tags like python objects with all standard html attributes
        # First parameter is the InnerHTML of the tag
        tags.h1(self.value, class_="my-class")
        # If we want add another html tags to innnerHTML, we can use "with" operator
        with tags.div(style="border: 1px solid black"):
            # This span is child of the div
            tags.span(request.headers)

# Page initialize the dependencies for component rendering
# Page endpoint is also a FastAPI endpoint
@router.page("/{name}")
def root(name: str):
    with tags.div(class_="container mt-6"):
        # This component initialization embed HTMX div and trigger the view method only after the div is rendered
        MyComponent(value=f"Hello, World from {name}")

# We can embed the router in a FastAPI app
app = FastAPI()
app.include_router(router)
```


## Documentation

Coming soon.


## License

Renderable is licensed under the [MIT License](https://github.com/nikirg/renderable/blob/main/LICENSE).