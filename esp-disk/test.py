from config import (
    SDA_PIN, SCL_PIN
)

from app.modules import Display
from app.services import Ui
from app.vues import BootVue








if __name__ == "__main__":
    display = Display(sda=SDA_PIN, scl=SCL_PIN)
    ui = Ui(display)

    ui.load_vue(
        BootVue()
    )

    while True:
        ui.update()