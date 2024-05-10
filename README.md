# Pyfront

Pyfront is a Python library designed for building modern web interfaces using a component-based approach inspired by popular JavaScript frameworks and the declarative coding style of Streamlit. With server-side rendering powered by HTMX, Pyfront allows developers to create rich, interactive web interfaces entirely in Python.

## Features

- **Component-Based**: Like modern JavaScript frameworks, Pyfront utilizes a component-based architecture to make your codebase cleaner and more modular.
- **Server-Side Rendering**: Powered by HTMX, components can be dynamically loaded and updated on the client side without needing a full page reload.
- **FastAPI Integration**: Built to work seamlessly with FastAPI, enabling rapid development and high performance. Additionally, Pyfront leverages FastAPI's full support for asynchronous operations.
- **Pure Python**: All front-end code is written in Python, eliminating the need to switch between languages and allowing Python developers to leverage their existing skills.

## Installation

To install Pyfront, run the following command in your terminal:

```bash
pip install pyfront
```

## Quick Start
Here's a simple example to get you started with Pyfront:

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse


import pyfront as pf

app = FastAPI()

class UserList(pf.Component):
    group: GROUP_TYPE

    async def view(self):
        users = get_user_by_group(self.group)

        for user in users:
            pass

class Page(pf.Component):
    title: str = "Pyfront example"

    async def view(self):
        pf.h1(self.title)

        pf.select()

        with pf.table():
            pf.HTMX.wrap(UserList(group=))
            
```
```sh
uvicorn example.main:app --reload --timeout-graceful-shutdown 3 --host 0.0.0.0
```

## Documentation
For more detailed documentation, including API reference and advanced usage examples, visit Pyfront Documentation.

## Contributing
We welcome contributions from the community, whether it's adding new features, improving documentation, or reporting bugs. Please see our Contributing Guidelines for more details on how to contribute to Pyfront.

## License
Pyfront is released under the MIT License. See the LICENSE file for more details.