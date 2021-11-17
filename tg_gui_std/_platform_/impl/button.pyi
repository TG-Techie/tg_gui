from typing import *

from tg_gui_core import Color
from ... import Button
from . import Native, SizeHint

def format_class(cls: Type[Button]) -> Type[Button]:
    """
    @decorator
    A tie-in to allow modification of the tg-gui class body
    for implemention specific mods
    :param cls: the tg-gui class object, to format
    :return: the same class
    """
    ...

def build(
    widget: Button,
    *,
    radius: int,
    size: float | int,
    fit_to_text: bool,
) -> tuple[Native, SizeHint]:
    """
    Creates the native element for the std tg-gui widget based on the _fixed_style_attrs_.
    Those _fixed_style_attrs_ are passed as kwargs to this function.
    :param widget: the tg-gui widget instance to build the native for
    :param **style_attrs: the fixed style attributes that are set at build time
    :return: a tuple of the native widget and suggested size
    """
    ...

def set_size(widget: Button, native: Native, width: int, height: int) -> None:
    """
    A tie-in to set the size of the native element based on the size hint and fixed style
    :param widget:
    :param width:
    :param height:
    """
    ...

def apply_style(
    widget: Button,
    native: Native,
    *,
    fill: Color,
    text: Color,
    active_fill: Color,
    active_text: Color,
) -> None:
    """
    formats the native widget with style attribute given.
    These are defined in the _stateful_style_attrs_ in the std class.
    :param widget: the tg-gui widget instance
    :param native: the imple native element to apply style to
    :param **style_attrs: the stateful style attributes being applied
    :return: nothing
    """
    ...
