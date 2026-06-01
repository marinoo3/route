from config import (
    SDA_PIN, SCL_PIN,
    API_URL, API_KEY, PUSH_FRECENCY_SEC,
    DEVICE_ID
)

from app.modules import IMUSensor, Display
from app.services import API, SimpleAPI
from app.controller import Controller

import machine





def main():
    """
    Init services and modules then run main loop
    """
    # ------- Services
    
    api = SimpleAPI(
        base_url=API_URL,
        api_key=API_KEY,
        device_id=DEVICE_ID
    )
    
    # -------- Modules

    imu = IMUSensor(sda=SDA_PIN, scl=SCL_PIN, target_hz=20)
    imu.configure(acc_divisor=31, gyro_divisor=31)  # ~35.2 Hz internal

    display = Display(sda=SDA_PIN, scl=SCL_PIN)

    # -------- Control

    controller = Controller(
        imu=imu,
        display=display,
        api=api,
        push_frecency_sec=PUSH_FRECENCY_SEC
    )

    # --------- Init

    print("Calibrating gyro, keep still..")
    imu.calibrate_gyro_bias()
    print("Done")

    print("Create route session")
    session_id = api.create_session()
    api.start()
    print(session_id)

    # --------- Main loop
    
    while True:
        imu.wait_next_tick()
        controller.step()




if __name__ == "__main__":    
    try:
        main()
    except KeyboardInterrupt:
        print("Exit")
    # except Exception as e:
    #     print("Exit on error:", e)
    #     machine.reset()


