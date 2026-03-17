from fastapi import Depends

from lazyfast import Component, tags
from website.routers.home import home_router, HomeState, FEATURES, SNIPPETS


@home_router.component(id="features-grid")
class FeaturesGrid(Component):
    async def view(self, state: HomeState = Depends(HomeState)):
        with tags.div(class_="feature-grid"):
            for i, (icon, title, desc) in enumerate(FEATURES):
                active = i == state.selected
                card_cls = "feature-card active" if active else "feature-card"
                with tags.div(class_=card_cls):
                    btn = tags.button("", id=f"feat-{i}", class_="card-select-btn")
                    if btn.trigger:
                        async with state:
                            state.selected = i
                    tags.div(icon, class_="icon")
                    tags.h3(title)
                    tags.p(desc)

        with tags.div(class_="feature-snippet"):
            with tags.div(class_="code-panel"):
                with tags.div(class_="panel-header"):
                    with tags.span(class_="panel-dots"):
                        tags.span(class_="dot red")
                        tags.span(class_="dot yellow")
                        tags.span(class_="dot green")
                    tags.span("example.py", class_="panel-filename")
                with tags.pre():
                    tags.code(SNIPPETS[state.selected], class_="language-python")
