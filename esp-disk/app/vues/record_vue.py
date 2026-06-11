from app.libs.micropython_ssd1306 import SSD1306_I2C

from app.vues.base import Vue
from app.vues.elements import DisplayElement, Console

TYPE_CHECKING = False
if TYPE_CHECKING:
    from app.modules import Display


class RecordVue(Vue):

    # Blink state for the REC indicator.
    _rec_tick: int = 0
    _REC_BLINK: int = 40

    def _logic_loop(self) -> None:
        return super()._logic_loop()

    # ------- RENDERER

    def _rec_renderer(
            self,
            oled: SSD1306_I2C,
            rx: int, ry: int, rw: int, rh: int,
            rvalue: dict
        ):
        """
        Blinking REC status renderer

        Args:
            oled (SSD1306_I2C): Oled display
            rx (int): Position x
            ry (int): Position y
            rw (int): Width
            rh (int): Height
            rvalue (Any): Value to render
        """
        size = 6
        pad = 2

        # Blink only the square, toggling every _REC_BLINK frames.
        if (self._rec_tick // self._REC_BLINK) % 2 == 0:
            oled.rect(rx, ry + 1, size, size, 1, True)

        # Static label next to the square.
        oled.text("REC", rx + size + pad, ry, 1)

        self._rec_tick += 1

    # ------- EVENT HANDLER

    def _handle_start(self, display: "Display") -> None:
        """
        Handle start recording
        """
        display.remove_element("new")
        print("starting")

        display.add_element(
            "rec",
            DisplayElement(
                "rec", 
                x=128-32, y=0, width=32, height=8,
                renderer=self._rec_renderer)
        )
    
    # ------- VUE LOADING

    def load(self, display: "Display") -> None:
        display.add_element(
            "new",
            Console(
                "new",
                0, 0, 128, 32,
                value={
                    'message': "New route",
                    'action': "Start"
                }
            )
        )

        self.bind(
            "start",
            lambda: self._handle_start(display),
            once=True
        )