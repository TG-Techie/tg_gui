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

# inject a bad value in for tg_gui_std during tg_gui_core startup
import sys

sys.modules["tg_gui_std"] = type(
    "ImportNotAlloedYet",
    (),
    dict(
        __repr__=lambda self: f"<ImportNotAlloedYet {self._name}>",
        __init__=lambda self, name: setattr(self, "_name", name),
    ),
)("tg_gui_std")

# -- start exposed api imports ---

# base classes and application environment
from ._shared import (
    uid,
    UID,
    clamp,
)
from .base import (
    Widget,
    color,
    Color,
    isoncircuitpython,
    singleinstance,
    application,
    NestingError,
    PlacementError,
    RenderError,
)

from .stateful import State, DerivedState

from .container import (
    Container,
    # self,
    # superior
    # app,
)
from .position_specifiers import (
    PositionSpecifier,
    ConstantPosition,
    centerto,
    leftof,
    rightof,
    below,
    above,
    center,
    top,
    bottom,
    left,
    right,
)
from .dimension_specifiers import (
    DimensionSpecifier,
    DimensionExpression,
    DimensionExpressionConstructor,
    ratio,
    height,
    width,
)


# --- std lib and impl tool ---
# classes and functions for making widget classes
from .base import _Screen_
from .container import (
    _bulitin_tg_specifiers_,
    declarable,
    isdeclarable,
)
from .root_widget import Root
from .specifiers import (
    SpecifierReference,
    Specifier,
    AttributeSpecifier,
    ForwardMethodCall,
    specify,
)
from ._shared import (
    ConstantGroup,
    Constant,
)

# un-injct (deject?) the bad import value
sys.modules.pop("tg_gui_std")
