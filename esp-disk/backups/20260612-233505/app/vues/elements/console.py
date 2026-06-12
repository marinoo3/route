from app.libs.micropython_ssd1306 import SSD1306_I2C

from app.vues.elements import DisplayElement

class Console(DisplayElement):


    def _default_renderer(
            self,
            oled: SSD1306_I2C, 
            rx: int, ry: int, rw: int, rh: int, 
            rvalue: dict
        ):
        """
        Render a log element

        Args:
            oled (SSD1306_I2C): Oled display
            rx (int): Position x
            ry (int): Position y
            rw (int): Width
            rh (int): Height
            rvalue (Any): Value to render
        """
        oled.rect(rx, ry, rw, 12, 1, True)
        oled.text(rvalue['message'].upper(), rx+2, ry+2, 0)

        console: list = rvalue.get('console', [])
        for i, line in enumerate(console):
            oled.text(str(line), rx, ry + 16 + 8*i)

        action = rvalue.get('action', None)
        if action:
            left = (rx + rw) - len(action) * 8
            oled.text(action.upper(), left, ry+rh-8)