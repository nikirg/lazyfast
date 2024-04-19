from abc import ABC
from enum import Enum
from typing import Any, Type, Literal, Callable
from dataclasses import dataclass, field

from pyfront.context import CURRENT_COMPONENT, CURRENT_PARENT_ELEMENT


ATTR_RENAME_MAP = {"class_": "class", "dir_": "dir", "async_": "async", "type_": "type"}

FIELDS_TO_EXCLUDE = ("content", "parent_element", "_children", "_self_closing")


__all__ = [
    "div",
    "span",
    "p",
    "ul",
    "ol",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "a",
    "table",
    "thead",
    "tbody",
    "tr",
    "td",
    "th",
    "script",
    "footer",
    "header",
    "form",
    "input",
    "button",
    "label",
    "select",
    "textarea",
    "option",
    "optgroup",
    "title",
    "meta",
    "link",
    "script",
    "meta",
    "html",
    "head",
    "body",
    "meta",
    # "style",
    # "base",
    "link",
    "meta",
    "caption",
]


class Dir(str, Enum):
    LTR = "ltr"
    RTL = "rtl"
    AUTP = "auto"


class Dropzone(str, Enum):
    COPY = "copy"
    MOVE = "move"
    LINK = "link"


# TODO: increse Lang enumeration


class Lang(str, Enum):
    EN = "en"
    RU = "ru"


class Translate(str, Enum):
    YES = "yes"
    NO = "no"


class Target(str, Enum):
    SELF = "_self"
    BLANK = "_blank"
    PARENT = "_parent"
    TOP = "_top"


class Crossorigin(str, Enum):
    ANONYMOUS = "anonymous"
    USE_CREDENTIALS = "use-credentials"


class MediaTypes(str, Enum):
    ALL = "all"
    PRINT = "print"
    SCREEN = "screen"
    SPEECH = "speech"


class Enctype(str, Enum):
    APPLICATION_X_WWW_FORM_URLENCODED = "application/x-www-form-urlencoded"
    MULTIPART_FORM_DATA = "multipart/form-data"
    TEXT_PLAIN = "text/plain"


class HTTPMethod(str, Enum):
    GET = "get"
    POST = "post"


@dataclass(slots=True)
class HTMLElement(ABC):
    content: str | None = None

    class_: str | None = None
    id: str | None = None
    style: str | None = None
    title: str | None = None
    role: str | None = None
    dataset: dict[str, Any] | None = None
    accesskey: str | None = None
    contenteditable: bool | None = None
    contextmenu: str | None = None
    dir_: Dir | None = None
    draggable: bool | None = None
    dropzone: Dropzone | None = None
    hidden: bool | None = None
    lang: Lang | None = None
    spellcheck: bool | None = None
    tabindex: int | None = None
    translate: Translate | None = None
    aria_labelledby: str | None = None
    aria_expand: str | None = None
    aria_controls: str | None = None

    # Events
    onblur: str | None = None
    onchange: str | None = None
    onclick: str | None = None
    ondbclick: str | None = None
    onfocus: str | None = None
    onkeydown: str | None = None
    onkeypress: str | None = None
    onkeyup: str | None = None
    onload: str | None = None
    onmousedown: str | None = None
    onmousemove: str | None = None
    onmouseout: str | None = None
    onmouseover: str | None = None
    onmouseup: str | None = None
    onunload: str | None = None

    hx: Type["HTMX"] | None = None

    # TODO: xml:lang
    # TODO: aria-*
    # TODO: classes to class after self.html()
    # TODO: data-* attributes
    # TODO: itemid, itemprop, itemref, itemscope, itemtype

    _self_closing: bool = field(default=False, init=False)
    _children: list[Type["HTMLElement"] | Type["Component"]] = field(
        default_factory=list
    )

    def __post_init__(self):
        if parent := CURRENT_PARENT_ELEMENT.get():
            parent.add_child(self)
            CURRENT_PARENT_ELEMENT.set(parent)
        elif comp := CURRENT_COMPONENT.get():
            comp.add_elm(self)
            CURRENT_COMPONENT.set(comp)
        else:
            raise RuntimeError(
                'Elements can be created only in the "view" method of an object of the Component class'
            )

    def __enter__(self):
        if self.content:
            raise TypeError(
                'You cannot use "with" operator and "content" field at the same time'
            )
        CURRENT_PARENT_ELEMENT.set(self)
        return self

    def __exit__(self, type, value, traceback):
        CURRENT_PARENT_ELEMENT.set(None)

    def add_child(self, elm: Type["HTMLElement"] | Type["Component"]):
        self._children.append(elm)

    @staticmethod
    def _build_attr_str_repr(key: str, value: Any) -> str:
        attr_name = ATTR_RENAME_MAP.get(key, key)
        attr_name = attr_name.replace("_", "-")
        if isinstance(value, bool):
            return f"{attr_name} "
        else:
            return f'{attr_name}="{value}" '

    def _get_attrs(self) -> str:
        attrs = ""
        for key in self.__dataclass_fields__:
            if key in FIELDS_TO_EXCLUDE:
                continue
            if value := getattr(self, key):
                if key == "dataset":
                    for data_key, data_value in value.items():
                        attrs += self._build_attr_str_repr(
                            "data-" + data_key, data_value
                        )
                elif key == "hx":
                    for hx_key, hx_value in value.attrs:
                        if hx_value:
                            attrs += self._build_attr_str_repr(hx_key, hx_value)
                else:
                    attrs += self._build_attr_str_repr(key, value)
        return attrs.strip()

    async def _build_content(self) -> str:
        content = ""
        for child in self._children:
            content += await child.html()
        return content

    async def html(self) -> str:
        tag_name = self.__class__.__name__.lower()
        attrs = self._get_attrs()
        if attrs:
            attrs = " " + attrs

        if self._self_closing:
            return f"<{tag_name}{attrs} />"
        else:
            content = self.content or await self._build_content()
            return f"<{tag_name}{attrs}>{content}</{tag_name}>"


class _Interactive:
    id: str | None = None


@dataclass(slots=True)
class div(HTMLElement):
    pass


@dataclass(slots=True)
class span(HTMLElement):
    pass


@dataclass(slots=True)
class p(HTMLElement):
    pass


@dataclass(slots=True)
class ul(HTMLElement):
    pass


@dataclass(slots=True)
class ol(HTMLElement):
    reversed_: bool | None = None
    start: int | None = None
    # TODO: type attribute


@dataclass(slots=True)
class li(HTMLElement):
    value: int | None = None


@dataclass(slots=True)
class h1(HTMLElement):
    pass


@dataclass(slots=True)
class h2(HTMLElement):
    pass


@dataclass(slots=True)
class h3(HTMLElement):
    pass


@dataclass(slots=True)
class h4(HTMLElement):
    pass


@dataclass(slots=True)
class h5(HTMLElement):
    pass


@dataclass(slots=True)
class h6(HTMLElement):
    pass


@dataclass(slots=True)
class a(HTMLElement):
    href: str | None = None
    rel: str | None = None
    type_: str | None = None
    # TODO: other atrributes


@dataclass(slots=True)
class caption(HTMLElement):
    pass


@dataclass(slots=True)
class colgroup(HTMLElement):
    pass


@dataclass(slots=True)
class col(HTMLElement):
    pass


@dataclass(slots=True)
class caption(HTMLElement):
    pass


@dataclass(slots=True)
class table(HTMLElement):
    pass


@dataclass(slots=True)
class thead(HTMLElement):
    pass


@dataclass(slots=True)
class tbody(HTMLElement):
    pass


@dataclass(slots=True)
class tfoot(HTMLElement):
    pass


@dataclass(slots=True)
class tr(HTMLElement):
    pass


@dataclass(slots=True)
class th(HTMLElement):
    abbr: str | None = None
    colspan: int | None = None
    rowspan: int | None = None
    headers: str | None = None
    scope: Literal["col", "colgroup", "row", "rowgroup"] | None = None


@dataclass(slots=True)
class td(HTMLElement):
    colspan: int | None = None
    rowspan: int | None = None
    headers: str | None = None


_referrerpolicy = Literal[
    "no-referrer",
    "no-referrer-when-downgrade",
    "same-origin",
    "origin",
    "origin-when-cross-origin",
    "unsafe-url",
]

_referrerpolicy = Literal[
    "no-referrer",
    "no-referrer-when-downgrade",
    "same-origin",
    "origin",
    "origin-when-cross-origin",
    "unsafe-url",
]


@dataclass(slots=True)
class script(HTMLElement):
    src: str | None = None
    type: str | None = None
    async_: bool | None = None
    defer: bool | None = None
    integrity: str | None = None
    nonce: str | None = None
    referrerpolicy: _referrerpolicy | None = None  # type: ignore
    crossorigin: Literal["anonymous", "use-credentials"] | None = None
    integrity: str | None = None
    referrerpolicy: _referrerpolicy | None = None  # type: ignore


@dataclass(slots=True)
class link(HTMLElement):
    href: str | None = None
    rel: str | None = None
    type: str | None = None
    crossorigin: Literal["anonymous", "use-credentials"] | None = None
    integrity: str | None = None
    referrerpolicy: _referrerpolicy | None = None  # type: ignore


@dataclass(slots=True)
class meta(HTMLElement):
    name: str | None = None
    content: str | None = None
    charset: str | None = None
    http_equiv: str | None = None
    scheme: str | None = None


@dataclass(slots=True)
class html(HTMLElement):
    lang: Lang | None = None


@dataclass(slots=True)
class body(HTMLElement):
    lang: Lang | None = None


@dataclass(slots=True)
class head(HTMLElement):
    pass


@dataclass(slots=True)
class header(HTMLElement):
    pass


@dataclass(slots=True)
class footer(HTMLElement):
    pass


@dataclass(slots=True)
class title(HTMLElement):
    pass


@dataclass(slots=True)
class nav(HTMLElement):
    pass


@dataclass(slots=True)
class section(HTMLElement):
    pass


@dataclass(slots=True)
class form(HTMLElement):
    accept_charset: str | None = None
    action: str | None = None
    # TODO: autocomplete attribute
    enctype: Enctype | None = None
    method: HTTPMethod | None = None
    name: str | None = None
    # TODO: novalidate attribute
    target: Target | None = None

    onreset: Callable | None = None
    onselect: Callable | None = None
    onsubmit: Callable | None = None


_input_type = Literal[
    "button",
    "checkbox",
    "color",
    "date",
    "datetime-local",
    "email",
    "file",
    "hidden",
    "image",
    "month",
    "number",
    "password",
    "radio",
    "range",
    "reset",
    "search",
    "submit",
    "tel",
    "text",
    "time",
    "url",
    "week",
]


@dataclass(slots=True)
class input(HTMLElement):
    _self_closing = True

    type_: _input_type | None = None
    accept: str | None = None
    checked: bool | None = None
    disabled: bool | None = None
    maxlength: int | None = None
    name: str | None = None
    readonly: bool | None = None
    required: bool | None = None
    value: str | None = None
    placeholder: str | None = None

    def __post_init__(self):
        comp = CURRENT_COMPONENT.get()
        if comp:
            self.value = comp._inputs.get(self.name)
        super(input, self).__post_init__()


@dataclass(slots=True)
class button(HTMLElement):
    disabled: bool | None = None
    name: str | None = None
    type_: Literal["submit", "reset", "button"] | None = None
    value: str | None = None

    onclick: str | None = "reloadComponent(this)"


@dataclass(slots=True)
class label(HTMLElement):
    for_: str | None = None


@dataclass(slots=True)
class select(HTMLElement):
    autofocus: bool | None = None
    disabled: bool | None = None
    multiple: bool | None = None
    name: str | None = None
    required: bool | None = None
    size: int | None = None


@dataclass(slots=True)
class textarea(HTMLElement):
    name: str | None = None
    placeholder: str | None = None
    required: bool | None = None
    autofocus: bool | None = None
    cols: int | None = None
    rows: int | None = None
    disabled: bool | None = None
    maxlength: int | None = None
    readonly: bool | None = None
    dirname: str | None = None
    form: str | None = None
    wrap: Literal["hard", "soft"] | None = None
    
    def __post_init__(self):
        comp = CURRENT_COMPONENT.get()
        if comp:
            self.content = comp._inputs.get(self.name)
        super(textarea, self).__post_init__()


@dataclass(slots=True)
class option(HTMLElement):
    disabled: bool | None = None
    label: str | None = None
    selected: bool | None = None
    value: str | None = None


@dataclass(slots=True)
class optgroup(HTMLElement):
    disabled: bool | None = None
    label: str | None = None
