import uasyncio as asyncio

from app.models.event import Event
from app.modules import Display, Button
from app.vues.base import Vue



class Ui:
    vue: Vue
    
    def __init__(self, display: Display, button: Button) -> None:
        self.display = display
        self.button = button

        # Start button loop
        asyncio.create_task(self.button.run())

    def load_vue(self, vue: Vue) -> None:
        """
        Load a vue on UI

        Args:
            vue (Vue): Vue to load, child of Vue class
        """
        self.vue = vue
        self.vue.load(self.display)

    def dispatch_event(self, event: Event, flush = False) -> None:
        """
        dispatch event on current vue

        Args:
            event (Event): Event to dispatch
            flush (bool): Flush the event and trigger UI update. Default to False
        """
        self.vue.dispatch(event)
        if flush:
            self.update()

    def update(self) -> None:
        """
        Update the controls, ui and vue
        """
        self.vue.update()
        self.display.render(force_full=True)

    async def run(self) -> None:
        """
        Refresh the UI at 10 Hz. Schedule with asyncio.create_task().
        """
        while True:
            self.update()
            await asyncio.sleep(0.1)

