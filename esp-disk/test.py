from config import (
    SDA_PIN, SCL_PIN
)

from app.models import Event
from app.modules import Display
from app.services import Ui
from app.vues import BootVue

import time

import asyncio




async def main():

    display = Display(sda=SDA_PIN, scl=SCL_PIN)

    ui = Ui(display)
    

    ui.load_vue(
        BootVue()
    )

    ui.dispatch_event(Event("wifiFailed"))
    
    asyncio.create_task(ui.run())
    
    while True:
        await asyncio.sleep(1)

asyncio.run(main())

# ui.dispatch_event(Event("wifiConnection", ssid="marin"), flush=True)
# ui.update()
# time.sleep(1)
