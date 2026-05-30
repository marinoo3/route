from app.models import IMUSamplesBuffer
from app.modules import IMUSensor, Display
from app.services import API

import time


class Controller:

    def __init__(
            self,
            imu: IMUSensor,
            display: Display,
            api: API,
            push_frecency_sec: int
        ) -> None:
        self.imu = imu
        self.display = display,
        self.api = api
        self.push_frecency_ms = push_frecency_sec * 1000
        self.buffer = IMUSamplesBuffer()

    def _now(self) -> int:
        """
        Get current time in micro seconds

        Returns:
            int: Current time
        """
        return time.ticks_ms()

    def calibrate_imu(self) -> None:
        """
        Calibrate gyro bias
        """
        print('Calibrating, keep still...')
        self.imu.calibrate_gyro_bias()

    def step(self) -> None:
        """
        Controller logic step
        """
        # Collect and save IMU data on buffer
        sample = self.imu.read_sample()
        self.buffer.register_sample(sample)

        # Send buffer if it is time to do so
        if self._now() > self.buffer.timestamp_start + self.push_frecency_ms:
            self.api.send_buffer(self.buffer)
            self.buffer.clear()