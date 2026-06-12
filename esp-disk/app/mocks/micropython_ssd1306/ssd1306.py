"""
ssd1306_terminal.py – minimal SSD1306 emulator for CPython.

Usage (keep your ESP32 code unchanged):

    try:
        from ssd1306 import SSD1306_I2C          # real hardware
    except ImportError:
        from ssd1306_terminal import SSD1306_I2C # terminal mock

    display = SSD1306_I2C(128, 32, i2c=None)     # i2c ignored on host
    display.fill(0)
    display.text("Hello host!", 0, 0)
    display.show()

The module contains a tiny frame buffer implementation, a monospace 5×8 font,
and a terminal renderer that uses ANSI escape codes (clears the screen area and
hides the cursor while the emulator is active).  Call `display.deinit()` or let
the program exit normally to restore the cursor.
"""

from __future__ import annotations

import atexit
import string
import sys
import threading
from typing import Dict, Iterable, Optional, Sequence, Tuple


__all__ = (
    "SSD1306",
    "SSD1306_I2C",
    "SSD1306_SPI",
    "TerminalRenderer",
    "MockI2C",
)


def const(value: int) -> int:  # MicroPython compatibility helper
    return value


# -----------------------------------------------------------------------------
# Font (simple 5x8 block font, uppercase reused for lowercase)
# -----------------------------------------------------------------------------
_SIMPLE_FONT_SOURCE: Dict[str, Tuple[str, ...]] = {
    " ": ("00000",) * 8,
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100", "00000"),
    "%": ("11001", "11010", "00100", "01000", "10110", "00110", "00000", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101", "00000"),
    "'": ("00100", "00100", "00100", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010", "00000"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000", "00000"),
    ",": ("00000", "00000", "00000", "00000", "00000", "01100", "01100", "00100"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100", "00000"),
    "/": ("00001", "00010", "00100", "01000", "10000", "00000", "00000", "00000"),
    "0": ("01110", "10001", "10001", "10101", "10001", "10001", "01110", "00000"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110", "00000"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111", "00000"),
    "3": ("01110", "10001", "00001", "00110", "00001", "10001", "01110", "00000"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010", "00000"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110", "00000"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110", "00000"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000", "00000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110", "00000"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100", "00000"),
    ":": ("00000", "01100", "01100", "00000", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "00000", "01100", "01100", "00100"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000", "00000"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000", "00000"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100", "00000"),
    "@": ("01110", "10001", "10111", "10101", "10111", "10000", "01110", "00000"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001", "00000"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110", "00000"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110", "00000"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100", "00000"),
    "E": ("11111", "10000", "11110", "10000", "10000", "10000", "11111", "00000"),
    "F": ("11111", "10000", "11110", "10000", "10000", "10000", "10000", "00000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01110", "00000"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001", "00000"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110", "00000"),
    "J": ("00001", "00001", "00001", "00001", "10001", "10001", "01110", "00000"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001", "00000"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111", "00000"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001", "00000"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001", "00000"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110", "00000"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000", "00000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101", "00000"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001", "00000"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110", "00000"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100", "00000"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110", "00000"),
    "V": ("10001", "10001", "10001", "10001", "01010", "01010", "00100", "00000"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010", "00000"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001", "00000"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100", "00000"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110", "00000"),
    "\\": ("10000", "01000", "00100", "00010", "00001", "00000", "00000", "00000"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110", "00000"),
    "^": ("00100", "01010", "10001", "00000", "00000", "00000", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111", "00000"),
    "`": ("01000", "00100", "00010", "00000", "00000", "00000", "00000", "00000"),
    "{": ("00010", "00100", "00100", "01000", "00100", "00100", "00010", "00000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100", "00000"),
    "}": ("01000", "00100", "00100", "00010", "00100", "00100", "01000", "00000"),
    "~": ("00000", "01010", "10101", "00000", "00000", "00000", "00000", "00000"),
}

for _ch in string.ascii_lowercase:
    upper = _ch.upper()
    if upper in _SIMPLE_FONT_SOURCE:
        _SIMPLE_FONT_SOURCE[_ch] = _SIMPLE_FONT_SOURCE[upper]


def _rows_to_columns(rows: Sequence[str]) -> Tuple[int, ...]:
    width = len(rows[0])
    columns: list[int] = []
    for x in range(width):
        mask = 0
        for y, row in enumerate(rows):
            if y >= 8:
                break
            if row[x] == "1":
                mask |= 1 << y
        columns.append(mask)
    return tuple(columns)


_SIMPLE_FONT = {ch: _rows_to_columns(rows) for ch, rows in _SIMPLE_FONT_SOURCE.items()}


# -----------------------------------------------------------------------------
# Minimal frame buffer implementation (MONO_VLSB)
# -----------------------------------------------------------------------------
class FrameBuffer:
    MONO_VLSB = 0  # matches MicroPython constant

    def __init__(self, buffer: bytearray, width: int, height: int, fmt: int = MONO_VLSB):
        if fmt != self.MONO_VLSB:
            raise ValueError("Only MONO_VLSB framebuffers are supported in this mock.")
        self.buffer = buffer
        self.width = width
        self.height = height
        self.format = fmt

    # -- helpers -------------------------------------------------------------
    def _index(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        page = y // 8
        offset = page * self.width + x
        mask = 1 << (y & 0x07)
        return offset, mask

    # -- drawing primitives --------------------------------------------------
    def pixel(self, x: int, y: int, color: Optional[int] = None) -> int:
        loc = self._index(x, y)
        if loc is None:
            return 0
        offset, mask = loc
        if color is None:
            return 1 if (self.buffer[offset] & mask) else 0
        if color:
            self.buffer[offset] |= mask
        else:
            self.buffer[offset] &= ~mask & 0xFF
        return color

    def fill(self, color: int) -> None:
        value = 0xFF if color else 0x00
        for i in range(len(self.buffer)):
            self.buffer[i] = value

    def fill_rect(self, x: int, y: int, w: int, h: int, color: int) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.pixel(xx, yy, color)

    def rect(self, x: int, y: int, w: int, h: int, color: int, fill: bool = False) -> None:
        # framebuf.rect supports an optional fill flag: rect(x, y, w, h, c[, f]).
        if fill:
            self.fill_rect(x, y, w, h, color)
            return
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)

    def hline(self, x: int, y: int, w: int, color: int) -> None:
        for xx in range(x, x + w):
            self.pixel(xx, y, color)

    def vline(self, x: int, y: int, h: int, color: int) -> None:
        for yy in range(y, y + h):
            self.pixel(x, yy, color)

    def line(self, x0: int, y0: int, x1: int, y1: int, color: int) -> None:
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def scroll(self, dx: int, dy: int) -> None:
        original = bytes(self.buffer)
        self.fill(0)
        for y in range(self.height):
            for x in range(self.width):
                page = y // 8
                mask = 1 << (y & 0x07)
                offset = page * self.width + x
                if original[offset] & mask:
                    self.pixel(x + dx, y + dy, 1)

    def blit(self, other: "FrameBuffer", x: int, y: int, key: int = -1) -> None:
        for yy in range(other.height):
            for xx in range(other.width):
                color = other.pixel(xx, yy)
                if key == -1 or color != key:
                    self.pixel(x + xx, y + yy, color)

    # -- text ----------------------------------------------------------------
    def text(self, string: str, x: int, y: int, color: int = 1) -> None:
        cursor_x = x
        cursor_y = y
        origin_x = x
        for char in string:
            if char == "\n":
                cursor_x = origin_x
                cursor_y += 8
                continue
            glyph = _SIMPLE_FONT.get(char)
            if glyph is None:
                cursor_x += 6
                continue
            for col_offset, column_bits in enumerate(glyph):
                for bit in range(8):
                    if column_bits & (1 << bit):
                        self.pixel(cursor_x + col_offset, cursor_y + bit, color)
            cursor_x += len(glyph) + 1


# -----------------------------------------------------------------------------
# Terminal renderer
# -----------------------------------------------------------------------------
class TerminalRenderer:
    """Render the framebuffer to the terminal using ANSI escape codes."""

    CSI = "\x1b["

    def __init__(self, width: int, height: int, on_char: str = "█", off_char: str = " "):
        self.width = width
        self.height = height
        self.on_char = on_char
        self.off_char = off_char
        self._lock = threading.Lock()
        self._first_frame = True
        self._cursor_hidden = False
        atexit.register(self._restore_cursor)

    # -- helpers -------------------------------------------------------------
    def _hide_cursor(self) -> None:
        if not self._cursor_hidden:
            sys.stdout.write(self.CSI + "?25l")
            sys.stdout.flush()
            self._cursor_hidden = True

    def _restore_cursor(self) -> None:
        if self._cursor_hidden:
            sys.stdout.write(self.CSI + "?25h")
            sys.stdout.flush()
            self._cursor_hidden = False

    def _move_home(self) -> None:
        sys.stdout.write(self.CSI + "H")

    def _clear(self) -> None:
        sys.stdout.write(self.CSI + "2J")
        self._move_home()
        sys.stdout.flush()

    # -- public --------------------------------------------------------------
    def render(self, buffer: Sequence[int], invert: bool = False) -> None:
        lines: list[str] = []
        width = self.width
        height = self.height
        pages = height // 8
        for y in range(height):
            page = y // 8
            mask = 1 << (y & 0x07)
            offset = page * width
            row_chars = []
            for x in range(width):
                byte = buffer[offset + x]
                bit_on = (byte & mask) != 0
                if invert:
                    bit_on = not bit_on
                row_chars.append(self.on_char if bit_on else self.off_char)
            lines.append("".join(row_chars))
        frame = "\n".join(lines) + "\n"

        with self._lock:
            if self._first_frame:
                self._clear()
                self._hide_cursor()
                self._first_frame = False
            else:
                self._move_home()
            sys.stdout.write(frame)
            sys.stdout.flush()

    def blank(self) -> None:
        blank_line = self.off_char * self.width
        block = "\n".join(blank_line for _ in range(self.height)) + "\n"
        with self._lock:
            if self._first_frame:
                self._clear()
                self._hide_cursor()
                self._first_frame = False
            else:
                self._move_home()
            sys.stdout.write(block)
            sys.stdout.flush()

    def close(self) -> None:
        self._restore_cursor()


# -----------------------------------------------------------------------------
# SSD1306 emulator
# -----------------------------------------------------------------------------
class SSD1306(FrameBuffer):
    def __init__(
        self,
        width: int,
        height: int,
        external_vcc: bool = False,
        *,
        renderer: Optional[TerminalRenderer] = None,
        on_char: str = "█",
        off_char: str = " ",
    ):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self._renderer = renderer or TerminalRenderer(width, height, on_char, off_char)
        self._powered = True
        self._inverted = False
        self._contrast = 0xFF

        super().__init__(self.buffer, self.width, self.height, FrameBuffer.MONO_VLSB)
        self.init_display()

    # -- API compatible methods ---------------------------------------------
    def init_display(self) -> None:
        self.fill(0)
        self.show()

    def poweroff(self) -> None:
        self._powered = False
        self._renderer.blank()

    def poweron(self) -> None:
        if not self._powered:
            self._powered = True
            self.show()

    def contrast(self, contrast: int) -> None:
        self._contrast = max(0, min(0xFF, int(contrast)))

    def invert(self, invert: int) -> None:
        self._inverted = bool(invert & 1)
        self.show()

    def show(self) -> None:
        if not self._powered:
            return
        self._renderer.render(self.buffer, invert=self._inverted)

    # Hardware specific stubs kept for compatibility ------------------------
    def write_cmd(self, cmd: int) -> None:
        # Only here so existing code that calls it does not crash.
        pass

    def write_data(self, buf: Iterable[int]) -> None:
        pass

    def deinit(self) -> None:
        """Restore the terminal (call when you are done)."""
        self._renderer.close()


class MockI2C:
    """Very small stand-in used by the emulator (records transactions)."""

    def __init__(self):
        self.log: list[Tuple[str, int, bytes]] = []

    def writeto(self, addr: int, data: Sequence[int]) -> None:
        self.log.append(("writeto", addr, bytes(data)))

    def writevto(self, addr: int, chunks: Sequence[bytes]) -> None:
        payload = b"".join(bytes(chunk) for chunk in chunks)
        self.log.append(("writevto", addr, payload))


class SSD1306_I2C(SSD1306):
    def __init__(
        self,
        width: int,
        height: int,
        i2c: Optional[MockI2C] = None,
        addr: int = 0x3C,
        external_vcc: bool = False,
        **kwargs,
    ):
        self.i2c = i2c or MockI2C()
        self.addr = addr
        super().__init__(width, height, external_vcc, **kwargs)


class SSD1306_SPI(SSD1306):
    def __init__(
        self,
        width: int,
        height: int,
        spi=None,
        dc=None,
        res=None,
        cs=None,
        external_vcc: bool = False,
        **kwargs,
    ):
        # SPI pins are ignored in the emulator but kept for signature parity.
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        super().__init__(width, height, external_vcc, **kwargs)


# -----------------------------------------------------------------------------
# Quick self-test / demo
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import time

    display = SSD1306_I2C(128, 32)
    for i in range(60):
        display.fill(0)
        display.text("MicroPython", 0, 0)
        display.text("Host Preview", 0, 10)
        display.text(f"Counter: {i:02d}", 0, 22)
        display.show()
        time.sleep(0.15)

    display.deinit()