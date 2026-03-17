import asyncio

from fastapi import Depends

from lazyfast import Component, ReloadRequest, tags
from website.routers.docs import docs_router, DemoState

FRAMEWORKS = [
    "FastAPI", "Django", "Flask", "Starlette",
    "Litestar", "Tornado", "Falcon", "Sanic",
    "Bottle", "Pyramid", "Quart", "Robyn",
]


@docs_router.component(id="greeter-demo")
class GreeterDemo(Component):
    async def view(self, state: DemoState = Depends(DemoState)):
        with tags.form():
            tags.p("Your name", class_="form-label")
            inp = tags.input(
                class_="demo-input",
                name="gname",
                placeholder="Ada Lovelace",
                type_="text",
            )
            btn = tags.button("Say hello →", id="greet-btn", class_="form-btn")

            if btn.trigger:
                async with state:
                    state.greeter_name = inp.value or ""

        if state.greeter_name:
            with tags.div(style="margin-top:1rem; text-align:center;"):
                tags.h2(
                    f"Hello, {state.greeter_name}!",
                    style="font-size:1.5rem; font-weight:800; color:var(--violet); letter-spacing:-0.02em;",
                )
                tags.p(
                    "Powered by LazyFast — no JavaScript written.",
                    style="font-size:0.8rem; color:var(--muted); margin-top:0.25rem;",
                )


@docs_router.component(id="tags-demo")
class TagsDemo(Component):
    color: str = "violet"

    async def view(self):
        COLOR_MAP = {
            "violet": ("#7c3aed", "#ede9fe", "#ddd6fe"),
            "blue":   ("#2563eb", "#eff6ff", "#bfdbfe"),
            "green":  ("#16a34a", "#f0fdf4", "#bbf7d0"),
            "amber":  ("#d97706", "#fffbeb", "#fde68a"),
            "rose":   ("#e11d48", "#fff1f2", "#fecdd3"),
        }

        sel = tags.select(class_="tag-select", name="color", reload_on=["onchange"])
        with sel:
            for val in COLOR_MAP:
                tags.option(val.capitalize(), value=val, selected=(val == self.color))

        chosen = sel.value or self.color
        self.color = chosen
        text_c, bg_c, border_c = COLOR_MAP[chosen]

        with tags.div(class_="tag-box", style=f"background:{bg_c}; border:2px dashed {border_c};"):
            tags.h2("Hello, LazyFast!", style=f"color:{text_c}; margin-bottom:0.3rem; font-size:1.1rem;")
            tags.p("Build HTML in pure Python.", style=f"color:{text_c}; opacity:0.8; font-size:0.875rem;")
            tags.span(
                f"tags.div › tags.h2 › tags.p  ·  {chosen}",
                style=f"font-size:0.68rem; color:{text_c}; opacity:0.5; display:block; margin-top:0.5rem;",
            )


@docs_router.component(id="unsafe-html-demo")
class UnsafeHTMLDemo(Component):
    raw: bool = False

    async def view(self):
        with tags.div(class_="demo-btns", style="margin-bottom:1rem;"):
            safe_btn = tags.button("Escaped (safe)", id="safe-btn", class_="demo-btn secondary")
            raw_btn  = tags.button("Raw HTML",       id="raw-btn",  class_="demo-btn primary")

        if safe_btn.trigger: self.raw = False
        if raw_btn.trigger:  self.raw = True

        html = "<b>Bold</b>, <em>italic</em>, <span style='color:#7c3aed'>violet</span>"

        tags.p("Content string:", style="font-size:0.75rem; color:var(--muted); margin-bottom:0.3rem;")
        with tags.div(class_="tag-box", style="background:#f4f4f5; border:2px dashed #d4d4d8; font-size:0.78rem;"):
            tags.code(html)

        tags.p("Rendered output:", style="font-size:0.75rem; color:var(--muted); margin:0.75rem 0 0.3rem;")
        with tags.div(class_="tag-box", style="background:#fff; border:2px dashed var(--border);"):
            tags.div(html, allow_unsafe_html=self.raw)

        mode = "allow_unsafe_html=True — rendered as HTML" if self.raw else "allow_unsafe_html=False (default) — escaped"
        tags.span(mode, style="font-size:0.72rem; color:var(--muted); display:block; margin-top:0.5rem;")


@docs_router.component(id="counter-demo")
class CounterDemo(Component):
    count: int = 0

    async def view(self):
        tags.div(str(self.count), class_="counter-value")

        with tags.div(class_="demo-btns"):
            dec = tags.button("−", id="comp-dec", class_="demo-btn secondary")
            inc = tags.button("+", id="comp-inc", class_="demo-btn primary")
            rst = tags.button("↺", id="comp-rst", class_="demo-btn danger")

        if inc.trigger: self.count += 1
        if dec.trigger: self.count -= 1
        if rst.trigger: self.count = 0


@docs_router.component(id="params-demo")
class ComponentParamsDemo(Component):
    title: str = "My Card"
    edit: bool = False

    async def view(self):
        toggle = tags.button(
            "Switch to Edit" if not self.edit else "Done editing",
            id="toggle-mode",
            class_="demo-btn primary",
        )
        if toggle.trigger:
            self.edit = not self.edit

        tags.h3(self.title, style="margin-top:1rem; font-weight:700; font-size:1rem;")

        if self.edit:
            with tags.form():
                inp  = tags.input(class_="demo-input", style="margin-bottom:0.5rem;",
                                  name="title", placeholder="New title…")
                save = tags.button("Save", id="save-title", class_="demo-btn secondary", style="width:100%;")
                if save.trigger and inp.value:
                    self.title = inp.value
        else:
            tags.p(
                "Read-only mode — click Switch to Edit to change the title above.",
                style="color:var(--muted); font-size:0.875rem;",
            )


@docs_router.component(id="search-demo")
class LiveSearchDemo(Component):
    async def view(self):
        inp = tags.input(
            class_="demo-input",
            name="q",
            placeholder="Filter frameworks…",
            reload_on=["oninput"],
        )

        query = (inp.value or "").lower()
        results = [f for f in FRAMEWORKS if query in f.lower()]

        with tags.div(class_="search-results"):
            for name in results:
                with tags.div(class_="search-item"):
                    tags.span("→", class_="search-item-icon")
                    tags.span(name)
            if not results:
                tags.p("No results found.", class_="search-empty")


@docs_router.component(id="form-demo")
class FormsDemo(Component):
    async def view(self):
        feedback = tags.div()

        with tags.form():
            with tags.div(class_="form-field"):
                tags.p("Name", class_="form-label")
                name_inp = tags.input(class_="demo-input", style="margin-bottom:0", name="fname", placeholder="Ada Lovelace", type_="text")
            with tags.div(class_="form-field"):
                tags.p("Email", class_="form-label")
                email_inp = tags.input(class_="demo-input", style="margin-bottom:0", name="femail", placeholder="ada@example.com", type_="email")
            with tags.div(class_="form-field"):
                tags.p("Message", class_="form-label")
                msg_inp = tags.input(class_="demo-input", style="margin-bottom:0", name="fmsg", placeholder="Hello!", type_="text")
            btn = tags.button("Send message →", id="form-send", class_="form-btn")

            if btn.trigger:
                fname  = name_inp.value or ""
                femail = email_inp.value or ""
                fmsg   = msg_inp.value or ""
                if fname and femail and fmsg:
                    feedback.content = f"✓ Thanks {fname}! We'll reply to {femail}."
                    feedback.class_ = "form-success"
                else:
                    feedback.content = "✗ Please fill in all fields."
                    feedback.class_ = "form-error"


@docs_router.component(id="self-reload-demo")
class SelfReloadDemo(Component):
    running: bool = False
    value: int = 0

    async def view(self):
        with tags.div(class_="demo-btns", style="margin-bottom:1rem;"):
            start = tags.button("Start", id="start-btn", class_="demo-btn primary")
            stop  = tags.button("Stop",  id="stop-btn",  class_="demo-btn secondary")

        if start.trigger: self.running = True
        if stop.trigger:  self.running = False

        if self.running:
            self.value = __import__("random").randint(0, 999)

        tags.div(
            str(self.value) if self.running else "—",
            class_="counter-value",
        )
        tags.p(
            "Updating every second via self.reload()" if self.running else "Press Start",
            class_="sse-note",
        )

        if self.running:
            await asyncio.sleep(1)
            await self.reload()


@docs_router.component(id="indicator-demo")
class IndicatorDemo(Component):
    result: str = ""

    async def view(self):
        with tags.div(style="display:flex; align-items:center; gap:0.75rem;"):
            btn = tags.button(
                "Run slow operation",
                id="run-btn",
                class_="demo-btn primary",
                dataset={"htmx-indicator-class": "is-loading"},
            )
            tags.span("Processing…", is_indicator=True,
                      style="color:var(--muted); font-size:0.875rem;")

        if btn.trigger:
            await asyncio.sleep(1.5)
            self.result = "Done! Operation completed successfully."

        if self.result:
            tags.div(self.result, class_="form-success", style="margin-top:1rem;")
        else:
            tags.p(
                "Click the button — the spinner appears client-side while the 1.5 s request is in-flight.",
                style="color:var(--muted); font-size:0.8rem; margin-top:0.75rem;",
            )


@docs_router.component(id="reload-request-demo")
class ReloadRequestDemo(Component):
    async def view(self, req: ReloadRequest = Depends(ReloadRequest)):
        with tags.div(class_="demo-btns", style="margin-bottom:1.25rem;"):
            tags.button("Button A", id="btn-a", class_="demo-btn primary")
            tags.button("Button B", id="btn-b", class_="demo-btn secondary")
            tags.button("Button C", id="btn-c", class_="demo-btn danger")

        rows = [
            ("trigger_id",    req.trigger_id    or "—"),
            ("trigger_event", req.trigger_event or "—"),
            ("method",        req.method),
            ("session_id",    (req.session_id or "")[:8] + "…"),
        ]
        with tags.div(class_="req-info"):
            for key, val in rows:
                with tags.div(class_="req-row"):
                    tags.span(key, class_="req-key")
                    tags.span(val, class_="req-val")


@docs_router.component(id="state-display", reload_on=[DemoState.state_count])
class StateDisplay(Component):
    async def view(self, state: DemoState = Depends(DemoState)):
        with tags.div(class_="state-comp"):
            tags.p("Display", class_="state-comp-label")
            tags.p(str(state.state_count), class_="state-comp-value")


@docs_router.component(id="state-controls")
class StateControls(Component):
    async def view(self, state: DemoState = Depends(DemoState)):
        with tags.div(class_="state-comp"):
            tags.p("Controls", class_="state-comp-label")
            with tags.div(class_="state-controls"):
                dec = tags.button("−", id="state-dec", class_="demo-btn secondary")
                inc = tags.button("+", id="state-inc", class_="demo-btn primary")
                rst = tags.button("↺", id="state-rst", class_="demo-btn danger")

        if inc.trigger:
            async with state:
                state.state_count += 1
        if dec.trigger:
            async with state:
                state.state_count -= 1
        if rst.trigger:
            async with state:
                state.state_count = 0


@docs_router.component(
    id="append-list",
    swapping_method="append",
    reload_on=[DemoState.append_count],
)
class AppendList(Component):
    async def view(self, state: DemoState = Depends(DemoState)):
        with tags.div(class_="search-item", style="justify-content:space-between;"):
            tags.span(f"Item {state.append_count}")
            tags.span(
                f"append_count = {state.append_count}",
                style="font-size:0.72rem; color:var(--muted);",
            )


@docs_router.component(id="append-trigger")
class AppendTrigger(Component):
    async def view(self, state: DemoState = Depends(DemoState)):
        btn = tags.button("Add item", id="add-item", class_="demo-btn primary")
        if btn.trigger:
            async with state:
                state.append_count += 1
