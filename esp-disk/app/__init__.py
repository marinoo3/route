import _thread

_stdout_lock = _thread.allocate_lock()

def log(*args):
    with _stdout_lock:
        print(*args)
