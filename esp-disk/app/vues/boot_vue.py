from app.vues.base import Vue
from app.modules import Display


class BootVue(Vue):
        
    def _logic_loop(self) -> None:
        return super()._logic_loop()

    def load(self, display: Display) -> None:
        display.add_text("Hello world")
