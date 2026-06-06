from config import (
    SDA_PIN, SCL_PIN
)

from app.modules import Display
from app.services import Ui
from app.vues import BootVue

import time







display = Display(sda=SDA_PIN, scl=SCL_PIN)
ui = Ui(display)

ui.load_vue(
    BootVue()
)

ui.dispatch_event("calibrateGyro")
ui.update()
time.sleep(1)

ui.dispatch_event("createSession")
ui.update()
time.sleep(1)