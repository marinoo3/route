"""
machine.py – host-side mock of MicroPython's machine module (I2C + Pin).

Enough of the API is reproduced to run SSD1306 / SPI demos, unit tests, etc.
"""

from __future__ import annotations

from typing import Iterable, Optional, Sequence, Tuple


class Pin:
    IN = 0
    OUT = 1
    OPEN_DRAIN = 2

    PULL_UP = 0x10
    PULL_DOWN = 0x20

    def __init__(self, id_, mode=IN, pull=None, value: Optional[int] = None):
        self.id = id_
        self._mode = mode
        self._pull = pull
        self._value = 0
        if value is not None:
            self._value = 1 if value else 0

    # MicroPython’s API accepts positional args (mode, pull, value)
    def init(self, mode=None, pull=None, value: Optional[int] = None):
        if mode is not None:
            self._mode = mode
        if pull is not None:
            self._pull = pull
        if value is not None:
            self._value = 1 if value else 0
        return self

    def value(self, val: Optional[int] = None) -> int:
        if val is None:
            return self._value
        self._value = 1 if val else 0
        return self._value

    # In MicroPython you can call Pin like pin(1)/pin()
    __call__ = value

    def __repr__(self):
        return f"<Pin id={self.id!r} mode={self._mode} value={self._value}>"


class I2C:
    MASTER = 0
    SLAVE = 1  # not actually implemented—but provided for completeness.

    def __init__(self, id_, *, scl: Optional[Pin] = None, sda: Optional[Pin] = None, freq=400_000):
        self.id = id_
        self.scl = scl
        self.sda = sda
        self.freq = freq
        self.log: list[Tuple[str, int, bytes]] = []
        self._devices = {}

    # --- Device registration helper (host-only) ----------------------------
    def register_device(self, addr: int, device) -> None:
        """Attach a mock peripheral with read/write methods."""
        self._devices[addr] = device

    # --- MicroPython-compatible methods ------------------------------------
    def init(self, id_=None, *, scl=None, sda=None, freq=None):
        if id_ is not None:
            self.id = id_
        if scl is not None:
            self.scl = scl
        if sda is not None:
            self.sda = sda
        if freq is not None:
            self.freq = freq

    def deinit(self):
        pass

    def scan(self):
        return sorted(self._devices.keys())

    def writeto(self, addr: int, data: Sequence[int], stop=True):
        payload = bytes(data)
        self.log.append(("writeto", addr, payload))
        dev = self._devices.get(addr)
        if dev and hasattr(dev, "writeto"):
            dev.writeto(payload)
        return len(payload)

    def readfrom(self, addr: int, nbytes: int, stop=True) -> bytes:
        dev = self._devices.get(addr)
        if dev and hasattr(dev, "readfrom"):
            data = dev.readfrom(nbytes)
            self.log.append(("readfrom", addr, bytes(data)))
            return bytes(data)
        data = bytes([0] * nbytes)
        self.log.append(("readfrom", addr, data))
        return data

    def readfrom_mem(self, addr: int, memaddr: int, nbytes: int, *, addrsize=8) -> bytes:
        dev = self._devices.get(addr)
        if dev and hasattr(dev, "readfrom_mem"):
            data = dev.readfrom_mem(memaddr, nbytes, addrsize=addrsize)
            self.log.append(("readfrom_mem", addr, bytes([memaddr]) + bytes(data)))
            return data
        data = bytes([0] * nbytes)
        self.log.append(("readfrom_mem", addr, bytes([memaddr]) + data))
        return data

    def writeto_mem(self, addr: int, memaddr: int, data: Sequence[int], *, addrsize=8):
        payload = bytes([memaddr]) + bytes(data)
        self.log.append(("writeto_mem", addr, payload))
        dev = self._devices.get(addr)
        if dev and hasattr(dev, "writeto_mem"):
            dev.writeto_mem(memaddr, bytes(data), addrsize=addrsize)
        return len(data)

    def writevto(self, addr: int, vector: Iterable[bytes], stop=True):
        payload = b"".join(bytes(chunk) for chunk in vector)
        self.log.append(("writevto", addr, payload))
        dev = self._devices.get(addr)
        if dev and hasattr(dev, "writeto"):
            dev.writeto(payload)
        return len(payload)

    # Convenience for quick tests
    def clear_log(self):
        self.log.clear()

    def __repr__(self):
        return f"<I2C id={self.id} freq={self.freq}Hz devices={len(self._devices)}>"