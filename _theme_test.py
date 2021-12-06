from __future__ import annotations

from typing import (
    Type,
    ClassVar,
    TYPE_CHECKING,
    Iterable,
    Any,
    Optional,
    Union,
    Generic,
    TypeVar,
    ForwardRef,
)

T = TypeVar("T")

from enum import Enum, auto

Color = int

_NotFound = type("NotFound", (), {})()


class ResolutionError(AttributeError):
    pass


class State:
    def __init__(self, value) -> None:
        self._value = value

    def value(self, reader) -> Any:
        return self._value


class LabelSize(Enum):
    normal = auto()
    large = auto()


class LazyInheritedAttribute(Generic[T]):
    _climb_stack: list["Widget"] = []
    _climb_sentinel = object()

    def __init__(self, attrname: str, initial: T) -> None:
        # TODO: add doc string to decribe the funcitonality
        self._attrname = attrname
        self._priv_attrname = "_inherited_" + attrname + "_attr_"
        self._initial = initial

    def __repr__(self):
        return f"<InheritedAttribute: .{self._attrname}>"

    def __get__(self, owner: "Widget", ownertype: Type[object]) -> T:
        privname = self._priv_attrname

        # check that this attribute was initialized to the initial value in
        # the object's constructor, this is to enforce good behanvior
        assert hasattr(owner, privname), (
            f"`{owner}.{self._attrname}` attribute not initialized, "
            + f"inherited `{type(owner).__name__}.{self._attrname}` attributes must be "
            + f"initialized to the inital `{self._initial}` or some value"
        )

        privattr = getattr(owner, privname)
        if privattr is not self._initial:  # normal get behavior
            return privattr
        else:  # get the inherited attribute

            self._climb_stack.append(owner)

            heirattr = getattr(owner._superior_, self._attrname, self._climb_sentinel)

            if heirattr is self._climb_sentinel:
                raise AttributeError(
                    f"unable to inherit .{self._attrname} attribute on {self._climb_stack[0]},"
                    + f"\nclimbed up {self._climb_stack}"
                )
            else:
                self._climb_stack.pop(-1)

            if heirattr is not self._initial:
                setattr(owner, privname, heirattr)
            return heirattr

    def __set__(self, owner, value) -> None:
        setattr(owner, self._priv_attrname, value)


if TYPE_CHECKING:
    InheritedAttribute = Union[
        None,
        T,
        LazyInheritedAttribute[Union[T, None]],
    ]
else:
    InheritedAttribute = {"Theme": object}


if TYPE_CHECKING:
    from typing import Protocol
else:
    Protocol = {T: object}  # type: ignore


class ThemedAttribute:

    _attr_may_be_stateful: ClassVar[bool]

    name: str
    widtype: Type["StyledWidget"]
    allowed: type | tuple[type, ...] = object

    def __init__(
        self,
        name: str,
        widtype: Type["StyledWidget"],
        allowed: type | tuple[type, ...] = object,
    ) -> None:
        assert (
            type(self) is not ThemedAttribute
        ), f"cannot init a non-subclasses ThemedAttribute"
        self.name = name
        self.widtype = widtype
        assert issubclass(widtype, StyledWidget)

        self.allowed = allowed

    def __get__(self, owner: None | "StyledWidget", ownertype: Type["StyledWidget"]):
        if owner is None:
            return self
        assert owner is not None

        name = self.name
        maybe_stateful = self._attr_may_be_stateful

        inst_attr_dict = (
            owner._stateful_attrs_ if maybe_stateful else owner._build_attrs_
        )
        attr = inst_attr_dict.get(name, _NotFound)

        if attr is _NotFound:
            theme = owner._theme_
            assert theme is not None

            if maybe_stateful:
                attr = theme.getstatefulattr(self.widtype, name, owner)
            else:
                attr = theme.getbuildattr(self.widtype, name, owner)

        assert isinstance(attr, self.allowed), (
            f"{owner}.{name} found object of {type(attr)}, "
            + f"expected on of {self.allowed}"
        )

        return attr

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:X {self.widtype.__name__}.{self.name}>"


class ThemedBuildAttribute(ThemedAttribute):
    _attr_may_be_stateful = False


class ThemedStatefulAttribute(ThemedBuildAttribute):
    _attr_may_be_stateful = True


# if not TYPE_CHECKING:
def themedwidget(widcls: "Type['Widget']") -> "Type['Widget']":

    assert issubclass(
        widcls, StyledWidget
    ), f"{widcls} does not subclass {StyledWidget}, cannot use @themedwidget on non-styled widget"

    buildattrs = widcls._build_style_attrs_
    statefulattrs = widcls._stateful_style_attrs_

    assert buildattrs not in (
        matched_build_conflict:= cls if (buildattrs is cls._build_style_attrs_) else False for cls in Theme._required_
    ), (
        f"{widcls} missing the ._build_style_attrs_ class attribute, "
        + "@themedwidget classes require ._build_style_attrs_ attrs spec. "
        + f"(ie found a dict that belonges to {matched_build_conflict})"
    )

    assert not any(
         matched_stateful_conflict:= cls if (statefulattrs is cls._stateful_style_attrs_) else False for cls in Theme._required_
    ), (
        f"{widcls} missing the ._stateful_style_attrs_ class attribute, "
        + "@themedwidget classes require ._stateful_style_attrs_  attrs spec. "
        + f"(ie found a dict that belonges to {matched_stateful_conflict})"
    )

    for attr, allowed in buildattrs.items():
        setattr(widcls, attr, ThemedBuildAttribute(attr, widcls, allowed))

    for attr, allowed in statefulattrs.items():
        setattr(widcls, attr, ThemedStatefulAttribute(attr, widcls, allowed))

    Theme._required_.add(widcls)

    # widcls._build_style_attrs_ = {
    #     attr: styledattr._allowed
    #     for attr in dir(widcls)
    #     if isinstance(styledattr := getattr(widcls, attr), StyledAttribute)
    # }

    return widcls


if TYPE_CHECKING:
    themedwidget = lambda cls: cls


class Widget:

    _superior_: Optional["Widget"]

    _theme_: InheritedAttribute["Theme"] = LazyInheritedAttribute("_theme_", None)

    def __init__(self, _margin_: None | int = None, **styleattrs) -> None:

        # assert (  # that there are not extra keywords
        #     len(extras := set(styleattrs) - set(self._build_style_attrs_)) == 0
        # ), f"extra keyword argument{'s'*bool(len(extras) > 1)} {', '.join(name+'=' for name in extras)}"

        

        self._superior_ = None
        self._theme_ = None
        self._margin_ = None

        super().__init__()

    @classmethod
    def _allows_themed_build_attr_(cls, name: str) -> bool:
        descriptor = getattr(cls, name, None)
        return isinstance(descriptor, ThemedBuildAttribute)

    @classmethod
    def _allows_themed_stateful_attr_(cls, name: str) -> bool:
        return isinstance(getattr(cls, name, None), ThemedStatefulAttribute)


class StyledWidget(Widget):

    _build_style_attrs_: ClassVar[dict[str, type | tuple[type, ...]]] = {}
    _stateful_style_attrs_: ClassVar[dict[str, type | tuple[type, ...]]] = {}

    def __init__(self, _margin_:None|int=None, **styleattrs) -> None:
        
        self._build_attrs_ = buildatters = {
            name: styleattrs[name]
            for name in styleattrs
            if self._allows_themed_build_attr_(name)
        }

        self._stateful_attrs_ = statefulattrs = {
            name: styleattrs[name]
            for name in styleattrs
            if self._allows_themed_stateful_attr_(name)
        }

        assert (
            len(overlap := set(buildatters) & set(statefulattrs)) == 0
        ), f"conflicting themedattribute for arguments {overlap}... How!?"

        assert (
            len(extra := set(styleattrs) - set(buildatters) - set(statefulattrs)) == 0
        ), f"extra styles {extra}"

        super().__init__(_margin_=_margin_)

class Theme:
    _required_: set[Type["StyledWidget"]] = set()

    # defaults = {
    #     Widget: {"__margin__": 5},
    # }

    def __init__(
        self,
        *,
        margin: int,
        styling: dict[
            Type["StyledWidget"],
            tuple[
                dict[str, Any],
                dict[str, Any],
            ],
        ],
    ) -> None:

        
        assert (
            len(extra := set(styling) - set(self._required_)) == 0
        ), f"extra style_attrs {extra}"

        assert (
            len(missing := set(self._required_) - set(styling)) == 0
        ), f"missing style_attrs for {missing}"

        self._margin_ = margin
        self._source = styling

        # TODO: assert self._check_styles()


    def getbuildattr(
        self, widcls: Type[StyledWidget], name: str, debug_widget: None | Widget
    ):
        return self._get_attr(widcls, name, False, debug_widget=debug_widget)

    def getstatefulattr(
        self, widcls: Type[StyledWidget], name: str, debug_widget: None | Widget
    ):
        return self._get_attr(widcls, name, True, debug_widget=debug_widget)

    def _get_attr(
        self,
        widcls: Type[StyledWidget],
        name: str,
        is_stateful: bool,
        debug_widget: None | Widget,
    ) -> Any:

        pack = self._source.get(widcls, _NotFound)

        if pack is _NotFound:
            wid_dbg_str = "" if debug_widget is None else f"(from {debug_widget})"
            raise ResolutionError(
                f"{self} has not themse entries for {widcls} at all {wid_dbg_str}, is it themed?"
            )

        attrs = pack[1] if is_stateful else pack[0]

        value = attrs.get(name, _NotFound)
        if value is not _NotFound:
            return value
        else:
            kind = "stateful" if is_stateful else "build"
            wid_dbg_str = (
                f"on widget of type {widcls}"
                if debug_widget is None
                else f" on {debug_widget}"
            )
            raise ResolutionError(
                f"cannot resolve themed {kind} attribute .{name} {wid_dbg_str}"
            )


themedwidget(StyledWidget)


@themedwidget
class Text(StyledWidget):

    _build_style_attrs_ = {"fit": bool, "size": LabelSize}
    _stateful_style_attrs_ = {"color": Color}

    def __init__(self, text: str, **attrs) -> None:
        self._text = text
        super().__init__(**attrs)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {repr(self._text)}>"


@themedwidget
class Label(Text):
    _build_style_attrs_ = {"size": LabelSize}
    _stateful_style_attrs_ = {}

    def __init__(self, text: str, **attrs) -> None:
        assert "\n" not in text, f"labels may only by one line, "
        super().__init__(text, **attrs)


class Date(Label):
    def __init__(self, src: str, **attrs) -> None:
        src.format(hour="17", min="01")
        self._src = src
        super().__init__(src, **attrs)


class Container(Widget):
    def __init__(self, *wids: Widget) -> None:
        super().__init__(_margin_=0)
        self._nested_ = wids
        for wid in wids:
            wid._superior_ = self


class Root(Container):

    _theme_ = Theme(
        margin=5,
        styling={
            StyledWidget: ( {},   {} ),
            Text: (
                dict(fit=True, size=LabelSize.normal),
                dict(color=0xFFFFFF),
            ),
            Label: (
                dict(size=LabelSize.large),
                {},
            ),
        },
    )

    def __init__(self, wid: Widget) -> None:
        self._superior_ = None
        wid._superior_ = self
        self._nested_ = (wid,)


txt = Text("hello\nworld!")
lbl = Label("whitty title")
dt = Date("{hour}:{min}")

cntr = Container(txt, lbl, dt)
root = Root(cntr)
