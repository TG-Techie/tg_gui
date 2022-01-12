# The MIT License (MIT)
#
# Copyright (c) 2021 Jonah Yolles-Murphy (TG-Techie)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import annotations

from tg_gui_core import (
    Specifier,
    Color,
    StyledWidget,
    themedwidget,
)
from tg_gui_core.theming import BuildAttribute, StyledAttribute
from .platform._platform_ import button as _button_impl

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *


@_button_impl.format_class
# @themedwidget(
#     buildattrs={
#         "radius": int,
#         "size": int,
#         "fit_to_text": bool,
#     },
#     statefulattrs={
#         "fill": Color,
#         "foreground": Color,
#         "active_fill": Color,
#         "active_color": Color,
#     },
# )
@themedwidget
class Button(StyledWidget):
    _offer_priority_ = 0
    _reserve_space_ = True
    _self_sizing_ = True

    # impl tie-in
    _impl_build_ = _button_impl.build
    _impl_set_size_ = _button_impl.set_size
    _impl_apply_style_ = _button_impl.apply_style
    _use_sug_height_ = True

    radius = BuildAttribute[int]()
    size = BuildAttribute[int]()
    fit_to_text = BuildAttribute[bool]()

    fill = StyledAttribute[Color]()
    foreground = StyledAttribute[Color]()

    fill = StyledAttribute[Color]()
    foreground = StyledAttribute[Color]()
    active_fill = StyledAttribute[Color]()
    active_foreground = StyledAttribute[Color]()

    @property
    def _use_sug_width_(self) -> bool:
        return self.fit_to_text

    @property
    def text(self) -> str:
        return self._text

    def __init__(
        self,
        text,
        *,
        action: Callable[[], None],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._text = text
        self._action_src = action
        self._action_ = None

    def _on_nest_(self):
        super()._on_nest_()

        action = self._action_src
        if isinstance(action, Specifier):
            action = action._resolve_specified_(self)
        self._action_ = action
