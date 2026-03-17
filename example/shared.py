"""Shared nav helpers used by every example and the showcase."""

from lazyfast import tags

EXAMPLES: list[tuple[str, str]] = [
    ("/todo", "Todo List"),
    ("/btc", "BTC Price"),
    ("/search", "Live Search"),
    ("/users", "User Form"),
    ("/files", "File Upload"),
    ("/converter", "HTML → Python"),
    ("/chat", "Chat Bot"),
]

BULMA = "https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css"

NAV_STYLE = """
.lf-nav { position: sticky; top: 0; z-index: 100; }
.lf-nav .navbar-item.is-active {
    background: #363636; color: #fff !important; font-weight: 600;
}
"""


def common_head(title: str) -> None:
    tags.meta(charset="UTF-8")
    tags.title(title)
    tags.link(rel="stylesheet", href=BULMA)
    tags.style(NAV_STYLE)


def render_nav(current: str = "") -> None:
    with tags.nav(class_="navbar is-dark lf-nav", role="navigation"):
        with tags.div(class_="navbar-brand"):
            tags.a("⚡ LazyFast", class_="navbar-item has-text-weight-bold", href="/")
        with tags.div(class_="navbar-menu is-active"):
            with tags.div(class_="navbar-start"):
                for path, label in EXAMPLES:
                    cls = "navbar-item" + (" is-active" if path == current else "")
                    tags.a(label, class_=cls, href=path)
            with tags.div(class_="navbar-end"):
                with tags.div(class_="navbar-item"):
                    tags.a("← Home", class_="button is-light is-small", href="/")
