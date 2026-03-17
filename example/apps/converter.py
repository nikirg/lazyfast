"""
HTML → Python converter example.

Standalone:
    uv run --with uvicorn --with beautifulsoup4 -m examples.converter
    open http://localhost:8000/converter
"""

import html as html_lib

from fastapi import FastAPI

from lazyfast import LazyFastRouter, Component, tags
from lazyfast.tags import ATTR_RENAME_MAP
from example.apps.shared import common_head, render_nav


_INVERTED_ATTR_MAP = {v: k for k, v in ATTR_RENAME_MAP.items()}

EXAMPLE_HTML = """<div class="card">
  <h2 class="title">Hello, World!</h2>
  <p class="subtitle">This is a <strong>sample</strong> card.</p>
  <a href="/about" class="button">Learn more</a>
</div>"""


def _rename_attrs(attrs: dict) -> dict:
    return {_INVERTED_ATTR_MAP.get(k, k): v for k, v in attrs.items()}


def _parse_element(element, indent: int = 0) -> list[str]:
    code: list[str] = []
    pad = " " * indent
    if not element.name:
        return code
    tag_name = element.name
    attrs = _rename_attrs(element.attrs)
    attrs_str = ", ".join(
        f'{k}="{"  ".join(v) if isinstance(v, list) else v}"' for k, v in attrs.items()
    )
    if element.contents:
        open_ = f"with tags.{tag_name}({attrs_str}):" if attrs_str else f"with tags.{tag_name}():"
        code.append(f"{pad}{open_}")
        for child in element.contents:
            if isinstance(child, str):
                child = child.strip()
                if child:
                    suffix = f", {attrs_str}" if attrs_str else ""
                    code.append(f"{pad}    tags.{tag_name}('{child}'{suffix})")
            else:
                code.extend(_parse_element(child, indent + 4))
    else:
        code.append(f"{pad}tags.{tag_name}({attrs_str})" if attrs_str else f"{pad}tags.{tag_name}()")
    return code


def html_to_python(raw_html: str) -> str:
    from bs4 import BeautifulSoup  # lazy: installed via --with beautifulsoup4

    soup = BeautifulSoup(raw_html, "html.parser")
    code: list[str] = []
    for el in soup.contents:
        if isinstance(el, str):
            el = el.strip()
            if el:
                code.append(f"tags.raw('{el}')")
        else:
            code.extend(_parse_element(el))
    return "\n".join(code)


router = LazyFastRouter(loader_route_prefix="/__lf_converter__")


@router.component()
class Converter(Component):
    async def view(self):
        with tags.div(class_="box"):
            tags.p("Paste HTML, get LazyFast code", class_="title is-5")
            with tags.form():
                with tags.div(class_="field"):
                    tags.label("HTML input", class_="label", for_="raw_html")
                    textarea = tags.textarea(
                        class_="textarea",
                        name="raw_html",
                        id="raw_html",
                        content=EXAMPLE_HTML,
                    )
                with tags.div(class_="field"):
                    tags.button("Convert", class_="button is-info", type_="submit")

            if raw_html := textarea.content:
                escaped = html_lib.escape(html_to_python(raw_html))
                tags.raw(
                    f'<pre style="background:#f5f5f5;padding:1rem;border-radius:4px;'
                    f'overflow-x:auto"><code>{escaped}</code></pre>'
                )


@router.page("/converter", head_renderer=lambda: common_head("HTML → Python"))
async def page():
    render_nav("/converter")
    with tags.div(class_="container mt-5"):
        Converter()


app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_graceful_shutdown=1)
