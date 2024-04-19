from typing import Any
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import pyfront as pf


with open("example/test.js", "r") as file:
    js_script = file.read()


class Form(pf.Component):
    async def view(self):
        # with pf.form():
        #     pf.h1("Form")
        #     pf.button("Submit", class_="button")
        #     pf.span(id="output")

        input_text = pf.textarea(class_="textarea", name="long_text")
        service_input = pf.input(id="service", type_="text", name="service")

        if input_text.content:
            pf.h2(input_text.content)
            input_text.content = None

        submit_btn = pf.button("Reload", id="submitBtn", class_="button is-primary")

        if self.reloaded_by(submit_btn):
            pf.div("RELOADED!")
            pf.div(input_text.content)


class Chat(pf.Component):
    name: str

    async def view(self):
        with pf.div(class_="container"):
            with pf.h3():
                pf.span(self.name)
                pf.input(type_="hidden", name="parent")
                pf.HTMX.wrap(Form())


class Page(pf.Component):
    title: str
    charset: str = "UTF-8"
    lang: str = "en"
    content: Any

    async def view(self):
        with pf.html(lang=self.lang):
            with pf.head():
                pf.meta(charset=self.charset)
                # @ TODO:
                # meta(name="viewport", content="width=device-width, initial-scale=1.0")
                pf.title(self.title)
                pf.link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css",
                )
                pf.script(src="https://unpkg.com/htmx.org@1.8.4")
                pf.script(js_script)

            with pf.body():
                self.content()



app = FastAPI()

pf.HTMX.configure(app)


@app.get("/")
async def root():
    page = Page(title="Pyfront", content=Chat(name="TON Foundation"))
    return HTMLResponse(await page.html())
