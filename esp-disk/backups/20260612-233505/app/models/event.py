import time


class Event:
    def __init__(
            self,
            name: str,
            **kwargs
        ) -> None:
        self.name = name
        self.data = kwargs or {}


class ClickEvent(Event):
    def __init__(
            self,
        ) -> None:
        self.name = "click"
        self.data: dict[str, int] = {
            'ts': time.ticks_ms()
        }