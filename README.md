# Renderable

Renderable is a lightweight Python library designed for building modern web interfaces using a component-based approach. It enables writing page logic on the server side in Python, integrating seamlessly with FastAPI. With Renderable, interactive elements like inputs, buttons, and selects trigger component reloads that occur on the server, updating the component's state dynamically.

## Key Features

1. **Component-Based Approach**: Build web interfaces using components that encapsulate logic, state, and presentation.
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
from typing import Literal
from fastapi import Depends
from pydantic import BaseModel

import renderable as rb

GROUP_TYPE = Literal["internal", "external"]

class User(BaseModel):
    id: int
    name: str
    group: GROUP_TYPE

class State(rb.State):
    group: GROUP_TYPE = "internal"

async def get_user_by_group(state: State = Depends(State.load)) -> list[User]:
    users = [
        User(id=1, name="John", group="external"),
        User(id=2, name="Alice", group="internal"),
        User(id=3, name="Anna", group="internal"),
        User(id=4, name="Sam", group="external"),
        User(id=5, name="Bob", group="internal"),
        User(id=6, name="Eve", group="external"),
        User(id=7, name="Mark", group="internal"),
        User(id=8, name="Kate", group="internal"),
        User(id=9, name="Tim", group="external"),
    ]
    return [user for user in users if user.group == state.group]

app = rb.RenderableApp(state_schema=State)

@app.component(id="userList", reload_on=[State.group])
async def UserList(users: list[User] = Depends(get_user_by_group)):
    with rb.table(class_="table"):
        with rb.thead():
            with rb.tr():
                rb.th("ID")
                rb.th("Name")

        with rb.tbody():
            for user in users:
                with rb.tr():
                    rb.td(user.id)
                    rb.td(user.name)

@app.component()
async def UserGroup(state: State = Depends(State.load)) -> None:
    groups: list[str] = ["internal", "external"]
    dataset = {"htmx-indicator-class": "is-loading"}

    with rb.div(class_="field"):
        rb.label("Select user group", class_="label", for_="group")

        with rb.div(class_="control"):
            with rb.div(class_="select", dataset=dataset):
                with rb.select(id="group", name="group") as group_select:
                    for group in groups:
                        rb.option(
                            group.capitalize(),
                            value=group,
                            selected=group == group_select.value,
                        )

    if group_select.value:
        async with state:
            state.group = group_select.value

def extra_head():
    rb.title("Renderable demo")
    rb.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )

@app.page("/{page_id}", head=extra_head)
async def root():
    with rb.div(class_="container mt-6"):
        with rb.div(class_="grid"):
            with rb.div(class_="cell"):
                with rb.div(class_="box"):
                    UserGroup()

            with rb.div(class_="cell"):
                with rb.div(class_="box"):
                    UserList()

```

## Usage

1. Define State: Use rb.State to manage the state of your application.
2. Create Components: Define components with the @app.component decorator. Components can depend on functions and other components.
3. Handle Interactions: Use form elements like rb.select, rb.input, and rb.button to capture user interactions.
4. Manage State: Use the state manager to trigger component reloads based on state changes.
5. Design Pages: Combine components into pages with the @app.page decorator.

## Documentation

For more detailed documentation and examples, please visit the official documentation site.

## Contributing

We welcome contributions! Please see our contributing guidelines for more information.


## License

Renderable is licensed under the MIT License.