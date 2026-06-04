"""
micropython.py – tiny host mock for the MicroPython helper module.

Only implements const(), which is enough for libraries like ssd1306.
"""

def const(value):
    """
    MicroPython's const() returns the integer argument unchanged but lets the
    cross‑compiler treat it as a compile-time constant.  On CPython we simply
    return the value.  Raise a TypeError for non-integers to mirror the
    firmware behaviour.
    """
    if not isinstance(value, int):
        raise TypeError("const() argument must be an integer")
    return value