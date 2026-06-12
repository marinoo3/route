# MICROPYTHON EMULATION
import uasyncio as asyncio

from config import (
    SDA_PIN, SCL_PIN, BTN_GPIO,
    SSID, PWD,
    API_URL, API_KEY, PUSH_FRECENCY_SEC,
    DEVICE_ID
)


from app.modules import IMUSensor, Display, Button
from app.services import API, Ui
from app.controller import Controller

import machine


async def main():
    """
    Init services and modules then run main loop
    """
    # ------- Services

    api = API(
        base_url=API_URL,
        api_key=API_KEY,
        device_id=DEVICE_ID
    )

    # -------- Modules

    imu = IMUSensor(sda=SDA_PIN, scl=SCL_PIN, target_hz=20)
    imu.configure(acc_divisor=31, gyro_divisor=31)  # ~35.2 Hz internal

    display = Display(sda=SDA_PIN, scl=SCL_PIN)
    button = Button(BTN_GPIO)
    ui = Ui(display, button)

    # -------- Control

    controller = Controller(
        imu=imu,
        ui=ui,
        api=api,
        push_frecency_sec=PUSH_FRECENCY_SEC,
        ssid=SSID,
        pwd=PWD
    )

    # --------- Init

    await controller.run()

    # await controller.boot()

    # while True:
    #     await controller.record()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
    # except Exception as e:
    #     print("Exit on error:", e)
    #     machine.reset()

