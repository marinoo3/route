# MICROPYTHON EMULATION
import uasyncio as asyncio

from config import (
    SDA_PIN, SCL_PIN,
    API_URL, API_KEY, PUSH_FRECENCY_SEC,
    DEVICE_ID
)

from app.modules import IMUSensor, Display
from app.services import AsyncAPI, Ui
from app.controller import Controller
from app.vues import BootVue

import machine


async def main():
    """
    Init services and modules then run main loop
    """
    # ------- Services

    api = AsyncAPI(
        base_url=API_URL,
        api_key=API_KEY,
        device_id=DEVICE_ID
    )

    # -------- Modules

    imu = IMUSensor(sda=SDA_PIN, scl=SCL_PIN, target_hz=20)
    imu.configure(acc_divisor=31, gyro_divisor=31)  # ~35.2 Hz internal

    display = Display(sda=SDA_PIN, scl=SCL_PIN)
    ui = Ui(display)

    # -------- Control

    controller = Controller(
        imu=imu,
        ui=ui,
        api=api,
        push_frecency_sec=PUSH_FRECENCY_SEC
    )

    # --------- Init
    
    ui.load_vue(
        BootVue()
    )

    session_task = asyncio.create_task(api.create_session())

    ui.dispatch_event("calibrateGyro")
    ui.update()
    imu.calibrate_gyro_bias()

    ui.dispatch_event("createSession")
    ui.update()
    await session_task
    
    ui.dispatch_event("done")
    ui.update()

    # --------- Main loop

    while True:
        imu.wait_next_tick()
        await controller.step()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
    # except Exception as e:
    #     print("Exit on error:", e)
    #     machine.reset()
