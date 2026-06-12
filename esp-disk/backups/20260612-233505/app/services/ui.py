
from config import UI_REFRESH_RATE
from app.models.event import Event
from app.modules import Display, Button
from app.vues.base import Vue

import uasyncio as asyncio
import time



class Ui:
    vue: Vue
    
    def __init__(self, display: Display, button: Button) -> None:
        self.display = display
        self.button = button
        self._render_done = asyncio.Event()

    def load_vue(self, vue: Vue) -> None:
        """
        Load a vue on UI

        Args:
            vue (Vue): Vue to load, child of Vue class
        """
        self.display.remove_all_elements()
        self.vue = vue
        self.vue.load(self.display)

    def dispatch_event(self, event: Event) -> None:
        """
        dispatch event on current vue

        Args:
            event (Event): Event to dispatch
        """
        self.vue.dispatch(event)

    def _now(self) -> int:
        """
        Get current unix in ms

        Returns:
            int: Now
        """
        return time.sleep_ms()
    
    def update(self) -> None:
        """
        Update UI
        """
        self.button.check_for_click()
        self.vue.update()
        self.display.render(force_full=True)

    async def run(self) -> None:
        """
        Refresh the UI at 10 Hz. Schedule with asyncio.create_task().
        """
        while True:
            tick = time.ticks_ms()
            self.update()
            delay = time.ticks_ms() - tick
            await asyncio.sleep(
                max(UI_REFRESH_RATE - delay, 0)
            )


