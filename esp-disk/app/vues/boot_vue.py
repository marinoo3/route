from app.vues.base import Vue
from app.modules import Display


class BootVue(Vue):
        
    def _logic_loop(self) -> None:
        return super()._logic_loop()

    def load(self, display: Display) -> None:
        display.add_text("message")

        self.bind(
            "calibrateGyro", 
            lambda: display.set_value("message", value="Calibrating...")
        )
        self.bind(
            "createSession", 
            lambda: display.set_value("message", value="Creating session...")
        )
        self.bind(
            "done", 
            lambda: display.set_value("message", value="Done")
        )