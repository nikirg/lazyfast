from bs4 import BeautifulSoup

from fastapi import FastAPI
from viewlet.tags import ATTR_RENAME_MAP
from viewlet import ViewletRouter, Component, tags

inverted_attr_rename_map = {v: k for k, v in ATTR_RENAME_MAP.items()}


def rename_attributes(attrs):
    return {inverted_attr_rename_map.get(k, k): v for k, v in attrs.items()}


def list_to_str(lst):
    return " ".join(lst)

def parse_element(element, indent=0):
    code = []
    indent_str = " " * indent

    if element.name:
        tag_name = element.name
        attrs = rename_attributes(element.attrs)
        attrs_str = ", ".join(
            f'{k}="{list_to_str(v) if isinstance(v, list) else v}"'
            for k, v in attrs.items()
        )

        if element.contents:
            if attrs_str:
                code.append(f"{indent_str}with tags.{tag_name}({attrs_str}):")
            else:
                code.append(f"{indent_str}with tags.{tag_name}():")
            for child in element.contents:
                if isinstance(child, str):
                    child = child.strip()
                    if child:
                        if attrs_str:
                            code.append(
                                f"{indent_str}    tags.{tag_name}('{child}', {attrs_str})"
                            )
                        else:
                            code.append(f"{indent_str}    tags.{tag_name}('{child}')")
                else:
                    code.extend(parse_element(child, indent + 4))
        else:
            if attrs_str:
                code.append(f"{indent_str}tags.{tag_name}({attrs_str})")
            else:
                code.append(f"{indent_str}tags.{tag_name}()")

    return code


def html_to_python(html):
    soup = BeautifulSoup(html, "html.parser")
    code = []
    for element in soup.contents:
        if isinstance(element, str):
            element = element.strip()
            if element:
                code.append(f"tags.raw('{element}')")
        else:
            code.extend(parse_element(element))
    return "\n".join(code)


router = ViewletRouter()


@router.component()
class Converter(Component):
    async def view(self):
        with tags.div(class_="container"):
            tags.h1("HTML to Viewlet", class_="title")
            with tags.form():
                with tags.div(class_="field"):
                    text_area = tags.textarea(class_="textarea", name="raw_html")
                with tags.div(class_="field"):
                    tags.button("Convert", class_="button", type_="submit")

            if raw_html := text_area.content:
                viewlet_code = html_to_python(raw_html)
                tags.div(
                    f"<pre>{viewlet_code}</pre>", class_="content", allow_unsafe_html=True
                )


def extra_head():
    tags.title("Converter")
    tags.link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
    )


@router.page("/", head=extra_head)
async def root():
    Converter()


app = FastAPI()
app.include_router(router)
