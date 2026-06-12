"""
atexit.py - host shim for the MicroPython unix port.

MicroPython has no `atexit` module.  The existing ssd1306 display mock registers
a callback to restore the terminal cursor on exit.  We record callbacks and,
when the unix port exposes `sys.atexit`, hook them so they still run on a clean
shutdown.  If `sys.atexit` is unavailable the callbacks simply never fire, which
is harmless (cursor restoration is cosmetic).
"""

import sys

_callbacks = []


def register(func, *args, **kwargs):
    _callbacks.append((func, args, kwargs))
    return func


def unregister(func):
    global _callbacks
    _callbacks = [cb for cb in _callbacks if cb[0] is not func]


def _run_all():
    while _callbacks:
        func, args, kwargs = _callbacks.pop()
        try:
            func(*args, **kwargs)
        except Exception:
            pass


# Hook the runtime's exit if the unix port supports it.
_sys_atexit = getattr(sys, "atexit", None)
if _sys_atexit is not None:
    _sys_atexit(_run_all)
