"""
threading.py - host shim for the MicroPython unix port.

MicroPython exposes low-level locks through `_thread` but has no `threading`
module.  The existing ssd1306 display mock only needs `threading.Lock()` (used
as a context manager), which maps directly onto `_thread.allocate_lock`.
"""

import _thread

# _thread locks already support acquire()/release() and the context-manager
# protocol, so allocate_lock is a drop-in for threading.Lock.
Lock = _thread.allocate_lock
RLock = _thread.allocate_lock


def get_ident():
    return _thread.get_ident()
