from abc import ABC
from dataclasses import dataclass, field, fields
from typing import Any, Callable, Literal, Type

from renderable import context
from renderable.htmx import HTMX

ATTR_RENAME_MAP = {
    "class_": "class",
    "dir_": "dir",
    "async_": "async",
    "type_": "type",
    "for_": "for",
}

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
    "h6",
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
    "dl",
    "dt",
    "blockquote",
    "strong",
]


# TODO: increse _lang enumeration

_lang = Literal["en", "ru", "es"]

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

tag_stack = context.StackManager[Type["Tag"]]("tag_stack")


@dataclass(slots=True)
class Tag(ABC):
    content: str | None = None

    id: str | None = None
    class_: str | None = None
    style: str | None = None
    title: str | None = None
    role: str | None = None
    dataset: dict[str, Any] | None = None
    accesskey: str | None = None
    contenteditable: bool | None = None
    contextmenu: str | None = None
    dir_: Literal["ltr", "rtl", "auto"] | None = None
    draggable: bool | None = None
    dropzone: Literal["copy", "move", "link"] | None = None
    hidden: bool | None = None
    lang: _lang | None = None
    spellcheck: bool | None = None
    tabindex: int | None = None
    translate: Literal["yes", "no"] | None = None
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

    # TODO: xml:_lang
    # TODO: aria-*
    # TODO: itemid, itemprop, itemref, itemscope, itemtype

    _self_closing: bool = field(default=False, init=False)
    _children: list[Type["Tag"]] = field(default_factory=list)

    def __str__(self):
        elms = []
        for f in fields(self):
            if value := getattr(self, f.tag_name):
                if f.tag_name == "_children":
                    elms.append("_children=[" + ",\t\n".join([child.__str__() for child in value]) + "]")
                else:
                    elms.append(f"{f.tag_name}={value!r}")
            
        return f"{self.tag_name}({', '.join(elms)})"

    @property
    def tag_name(self) -> str:
        return self.__class__.__name__.lower()

    @property
    def children(self) -> list[Type["Tag"]]:
        return self._children

    def add_child(self, tag: Type["Tag"]):
        self._children.append(tag)

    def clear_children(self):
        self._children = []

    def __enter__(self):
        if self._self_closing:
            raise TypeError('You cannot use "with" operator in a self-closing tag')
        if self.content:
            raise TypeError(
                'You cannot use "with" operator and "content" field at the same time'
            )
        tag_stack.append(self)
        return self

    def __exit__(self, *_):
        tag_stack.pop_last()

    def __post_init__(self):
        if parent_tag := tag_stack.get_last():
            parent_tag.add_child(self)
            tag_stack.update_last(parent_tag)

        elif component := context.get_component():
            component.add_tag(self)
            context.set_component(component)

        else:
            raise RuntimeError(
                "Tags can only be created within a method decorated with a @rb.Page or @rb.Component"
            )

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

    def _build_content(self) -> str:
        return "".join([tag.html() for tag in self._children])

    def html(self) -> str:
        attrs = self._get_attrs()
        if attrs:
            attrs = " " + attrs

        if self._self_closing:
            return f"<{self.tag_name}{attrs} />"
        else:
            content = self.content or self._build_content()
            return f"<{self.tag_name}{attrs}>{content}</{self.tag_name}>"


@dataclass(slots=True)
class div(Tag):
    pass


@dataclass(slots=True)
class span(Tag):
    pass


@dataclass(slots=True)
class p(Tag):
    pass


@dataclass(slots=True)
class ul(Tag):
    pass


@dataclass(slots=True)
class ol(Tag):
    reversed_: bool | None = None
    start: int | None = None
    type_: str | None = None


@dataclass(slots=True)
class li(Tag):
    value: int | None = None


@dataclass(slots=True)
class h1(Tag):
    pass


@dataclass(slots=True)
class h2(Tag):
    pass


@dataclass(slots=True)
class h3(Tag):
    pass


@dataclass(slots=True)
class h4(Tag):
    pass


@dataclass(slots=True)
class h5(Tag):
    pass


@dataclass(slots=True)
class h6(Tag):
    pass


@dataclass(slots=True)
class a(Tag):
    href: str | None = None
    rel: str | None = None
    type_: str | None = None
    # TODO: other atrributes


@dataclass(slots=True)
class caption(Tag):
    pass


@dataclass(slots=True)
class colgroup(Tag):
    pass


@dataclass(slots=True)
class col(Tag):
    pass


@dataclass(slots=True)
class caption(Tag):
    pass


@dataclass(slots=True)
class table(Tag):
    pass


@dataclass(slots=True)
class thead(Tag):
    pass


@dataclass(slots=True)
class tbody(Tag):
    pass


@dataclass(slots=True)
class tfoot(Tag):
    pass


@dataclass(slots=True)
class tr(Tag):
    pass


@dataclass(slots=True)
class th(Tag):
    abbr: str | None = None
    colspan: int | None = None
    rowspan: int | None = None
    headers: str | None = None
    scope: Literal["col", "colgroup", "row", "rowgroup"] | None = None


@dataclass(slots=True)
class td(Tag):
    colspan: int | None = None
    rowspan: int | None = None
    headers: str | None = None


@dataclass(slots=True)
class script(Tag):
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
class link(Tag):
    href: str | None = None
    rel: str | None = None
    type: str | None = None
    crossorigin: Literal["anonymous", "use-credentials"] | None = None
    integrity: str | None = None
    referrerpolicy: _referrerpolicy | None = None  # type: ignore


@dataclass(slots=True)
class meta(Tag):
    _self_closing = True
    
    name: str | None = None
    content: str | None = None
    charset: str | None = None
    http_equiv: str | None = None
    scheme: str | None = None


@dataclass(slots=True)
class html(Tag):
    lang: _lang | None = None


@dataclass(slots=True)
class body(Tag):
    lang: _lang | None = None


@dataclass(slots=True)
class head(Tag):
    pass


@dataclass(slots=True)
class header(Tag):
    pass


@dataclass(slots=True)
class footer(Tag):
    pass


@dataclass(slots=True)
class title(Tag):
    pass


@dataclass(slots=True)
class nav(Tag):
    pass


@dataclass(slots=True)
class section(Tag):
    pass


_enctype = Literal[
    "application/x-www-form-urlencoded", "multipart/form-data", "text/plain"
]


@dataclass(slots=True)
class form(Tag):
    accept_charset: str | None = None
    action: str | None = None
    # TODO: autocomplete attribute
    enctype: _enctype | None = None
    method: Literal["get", "post"] | None = None
    name: str | None = None
    # TODO: novalidate attribute
    target: Literal["_self", "_blank", "_parent", "_top"] | None = None

    onreset: Callable | None = None
    onselect: Callable | None = None
    onsubmit: Callable | None = None


@dataclass(slots=True)
class input(Tag):
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
    list: str | None = None

    def __post_init__(self):
        if comp := context.get_component():
            self.value = comp.inputs.get(self.name)
        super(input, self).__post_init__()


@dataclass(slots=True)
class button(Tag):
    disabled: bool | None = None
    name: str | None = None
    type_: Literal["submit", "reset", "button"] | None = None
    value: str | None = None

    onclick: str | None = "reloadComponent(this)"


@dataclass(slots=True)
class label(Tag):
    for_: str | None = None


@dataclass(slots=True)
class select(Tag):
    autofocus: bool | None = None
    disabled: bool | None = None
    multiple: bool | None = None
    name: str | None = None
    required: bool | None = None
    size: int | None = None

    onchange: str | None = "reloadComponent(this)"

    @property
    def value(self) -> Any:
        if comp := context.get_component():
            return comp.inputs.get(self.name)


@dataclass(slots=True)
class textarea(Tag):
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
        if comp := context.get_component():
            self.content = comp.inputs.get(self.name)
        super(textarea, self).__post_init__()


@dataclass(slots=True)
class option(Tag):
    disabled: bool | None = None
    label: str | None = None
    selected: bool | None = None
    value: str | None = None


@dataclass(slots=True)
class optgroup(Tag):
    disabled: bool | None = None
    label: str | None = None


@dataclass(slots=True)
class i(Tag):
    pass


@dataclass(slots=True)
class article(Tag):
    pass


@dataclass(slots=True)
class img(Tag):
    src: str | None = None
    alt: str | None = None
    width: int | None = None
    height: int | None = None
    crossorigin: Literal["anonymous", "use-credentials"] | None = None
    loading: Literal["eager", "lazy"] | None = None


@dataclass(slots=True)
class data(Tag):
    value: str | None = None


@dataclass(slots=True)
class datalist(Tag):
    pass


@dataclass(slots=True)
class dialog(Tag):
    open: bool | None = None


@dataclass(slots=True)
class dl(Tag):
    pass


@dataclass(slots=True)
class dt(Tag):
    pass


@dataclass(slots=True)
class em(Tag):
    pass


@dataclass(slots=True)
class blockquote(Tag):
    cite: str | None = None


@dataclass(slots=True)
class strong(Tag):
    pass


@dataclass(slots=True)
class canvas(Tag):
    width: int | None = None
    height: int | None = None
