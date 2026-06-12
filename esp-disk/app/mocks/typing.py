"""
typing.py - host shim for the MicroPython unix port.

MicroPython does not ship a `typing` module and never evaluates annotations at
runtime, so type hints in the application code are already harmless.  The only
thing that breaks is the literal `from typing import Dict, Optional, ...` lines
inside the existing CPython-style mocks.  This shim returns a subscriptable,
callable placeholder for any requested name, so those imports succeed and any
`Dict[str, Tuple[...]]` style expression still evaluates without error.
"""


class _Placeholder:
    """Subscriptable / callable stand-in for any typing construct."""

    def __getitem__(self, item):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __repr__(self):
        return "<typing-shim>"


_placeholder = _Placeholder()

# Explicit names so direct attribute access works even where module-level
# __getattr__ is unavailable.
Any = Optional = Union = ClassVar = Final = NoReturn = _placeholder
List = Dict = Tuple = Set = FrozenSet = Deque = _placeholder
Sequence = Iterable = Iterator = Mapping = MutableMapping = _placeholder
MutableSequence = MutableSet = AbstractSet = Collection = Container = _placeholder
Callable = Type = Generator = Coroutine = Awaitable = AsyncIterator = _placeholder
Hashable = Sized = Reversible = Generic = Protocol = _placeholder
Text = AnyStr = ByteString = SupportsInt = SupportsFloat = _placeholder

TYPE_CHECKING = False


def TypeVar(*args, **kwargs):
    return _placeholder


def NewType(name, tp):
    return tp


def cast(typ, val):
    return val


def get_type_hints(*args, **kwargs):
    return {}


def overload(func):
    return func


def no_type_check(func):
    return func


def __getattr__(name):
    # Catch-all for any name not defined above.
    return _placeholder
