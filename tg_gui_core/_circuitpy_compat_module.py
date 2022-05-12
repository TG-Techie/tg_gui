# ---- shared ----
import sys

import builtins

try:
    from typing import Any, TYPE_CHECKING
    from typing_extensions import LiteralString
except:
    pass
else:
    if not TYPE_CHECKING:
        assert (
            False
        ), f"the {__name__} module should not be imported except when on circuitpython"


class GetItemBypass:
    _value: Any  # type: ignore

    def __init__(self, name: str, value) -> None:
        self._name = name
        self._value = value

    def __getitem__(self, *_, **__):
        return self._value

    def __call__(self, *args, **kwds):
        return self._value(args, kwds)

    def __getattr__(self, name: LiteralString):
        return getattr(self._value, name)

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self._name} = {self._value}>"

    def _inst_isinstance_check_(self, *inst):
        if len(inst) == 1:
            inst = inst
        else:
            return False
        return isinstance(inst, self._value) or (
            hasattr(self._value, "__cp_compat_instancecheck__")
            and self._value.__cp_compat_instancecheck__(inst)
        )


# ---- module: typing ----

TYPE_CHECKING = False

# TODO: make this accept any number of index args


def Generic__new__(cls, *args, **kwds):
    assert getattr(
        cls, "__generic_compat__", False
    ), f"generic class {cls} not decorated with @generic_compat"
    return object.__new__(cls)


Generic = GetItemBypass(
    "Generic", type("Generic", (object,), {"__new__": Generic__new__})
)
Protocol = GetItemBypass("Protocol", type("Protocol", (object,), {}))

TypeVar = lambda *_, **__: None

# overload = (
#     lambda fn: None
#     if __debug__
#     else lambda fn: (
#         lambda *_, **__: _raise(
#             SyntaxError(
#                 f"overloaded only function defined, "
#                 + f"{fn.__globals__['__name__']}.{fn.__name__} is not defined without overloads"
#             )
#         )
#     )
# )

# ---- module: types ----
@type
def FunctionType():
    pass


LambdaType = type(lambda: None)

BuiltinFunctionType = type(print)

ModuleType = type(builtins)

Any = object

# ---- module: enum ----
# enum, auto, Enum


def auto():
    return None


def enum_compat(cls: type):
    for k, v in cls.__dict__.items():
        setattr(cls, k, cls(k, v))


class Enum:
    def __init__(self, name: str, value: object):
        self.value = value
        self.name = name


# ---- module: abc ----
# ABC, abstractmethod, abstractproperty


class ABC:
    pass


if __debug__:

    def _raise(e: Exception) -> None:
        raise e

    abstractmethod = lambda fn, *_, **__: (
        lambda *_, **__: _raise(
            NotImplementedError(
                f"{fn.__globals__['__name__']}.<class>.{fn.__name__}(...) not implemented"
            )
        )
    )

    abstractclassmethod = lambda fn, *_, **__: classmethod(abstractmethod(fn))
    abstractproperty = lambda fget, *_, **__: property(abstractmethod(fget))

else:
    abstractmethod = lambda fn: fn  # type: ignore[misc, assignment]
    abstractclassmethod = classmethod  # type: ignore[assignment]
    abstractproperty = property  # type: ignore[assignment]

# ---- module: __future__ ----
annotations = None

# ---- misc ----
# list of all modules this file replaces
__bypassed_modules__ = (
    "__future__",  # added in CP 7 ?
    "typing",
    "types",
    "enum",
    "abc",
)


GenericABC = GetItemBypass(
    "GenericABC", type("GenericABC", (object,), {"__new__": Generic__new__})
)


def load_bypassed_modules():
    this_module = sys.modules[__name__]
    for mod in __bypassed_modules__:
        sys.modules[mod] = this_module
