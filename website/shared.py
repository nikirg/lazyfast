from lazyfast import tags

HLJS_STYLE = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css"
HLJS_SCRIPT = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"


def head(title: str, hljs: bool = False):
    def _render():
        tags.meta(charset="UTF-8")
        tags.meta(name="viewport", content_="width=device-width, initial-scale=1")
        tags.title(f"{title} | LazyFast")
        tags.link(rel="stylesheet", href="/static/styles.css")
        if hljs:
            tags.link(rel="stylesheet", href=HLJS_STYLE)
            tags.script(src=HLJS_SCRIPT)
            tags.script("document.addEventListener('DOMContentLoaded', () => hljs.highlightAll());")
    return _render


def site_nav(current: str = "") -> None:
    with tags.nav(class_="site-nav"):
        tags.a("⚡ LazyFast", href="/", class_="logo")
        tags.a("Home", href="/")
        tags.a("Docs", href="/docs")
        tags.span(class_="spacer")
        tags.a("GitHub →", href="https://github.com/nikirg/lazyfast", class_="nav-cta")
