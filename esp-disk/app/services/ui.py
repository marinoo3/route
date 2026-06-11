import uasyncio as asyncio

from app.models.event import Event
from app.modules import Display, Button
from app.vues.base import Vue



class Ui:
    vue: Vue
    
    def __init__(self, display: Display, button: Button) -> None:
        self.display = display
        self.button = button
        self._render_done = asyncio.Event()

        # Start button loop
        asyncio.create_task(self.button.run())

    def load_vue(self, vue: Vue) -> None:
        """
        Load a vue on UI

        Args:
            vue (Vue): Vue to load, child of Vue class
        """
        self.display.remove_all_elements()
        self.vue = vue
        self.vue.load(self.display)

    def dispatch_event(self, event: Event, flush = False) -> None:
        """
        dispatch event on current vue

        Args:
            event (Event): Event to dispatch
            flush (bool): Render immediately (inline). Default False, so the event is only
                queued and rendered by Ui.run() / awaited via Ui.tick().
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

    async def tick(self) -> None:
        """
        Yield until Ui.run() has drained queued events and rendered one frame.

        Use this between blocking calls to force a repaint without rendering inline,
        e.g. after dispatch_event(..., flush=False).
        """
        self._render_done.clear()
        await self._render_done.wait()

    async def run(self) -> None:
        """
        Refresh the UI at 10 Hz. Schedule with asyncio.create_task().
        """
        while True:
            self.update()
            self._render_done.set()
            await asyncio.sleep(0.1)


