from app.models.event import ClickEvent

from machine import Pin
import time

class Button:
    debounce_ms = 50

    def __init__(self, gpio: int):
        """
        Build button

        Args:
            gpio (int): Button GPIO pin number
        """
        self.pin = Pin(gpio, Pin.IN, Pin.PULL_UP)

        self._last_state = self._read()
        self._last_change = time.ticks_ms()
        self.last_click: ClickEvent|None = None

    def _read(self) -> bool:
        """
        Read button state
        """
        value = self.pin.value()
        return not value
    
    def _save_click(self) -> None:
        """
        Create click event and save it as last click
        """
        self.last_click = ClickEvent()

    def check_for_click(self) -> None:
        """
        Read button state and update click if released
        """
        current = self._read()

        if current != self._last_state:
                now = time.ticks_ms()
                if time.ticks_diff(now, self._last_change) > self.debounce_ms:
                    self._last_change = now
                    self._last_state = current

                    if not current:
                        self._save_click()
