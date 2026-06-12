"""
__future__.py - host shim for the MicroPython unix port.

CPython special-cases `from __future__ import ...` in the compiler, so the
module body is irrelevant there.  MicroPython has no `__future__` module at
all, which makes any `from __future__ import annotations` line raise
ImportError.  Providing this tiny module turns that statement into an ordinary
(and harmless) attribute import, so the existing CPython-style mocks
(ssd1306.py, machine.py, ...) import unchanged.
"""

annotations = object()
division = object()
print_function = object()
absolute_import = object()
unicode_literals = object()
generator_stop = object()
with_statement = object()
nested_scopes = object()
generators = object()
