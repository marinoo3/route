from app.libs.micropython_icm20948 import icm20948
from app.models import IMUSample

from machine import Pin, I2C
import time



class IMUSensor:
    """
    High-level IMU wrapper around the ICM20948 driver.
    Designed for periodic polling around 50Hz.
    """

    def __init__(
        self,
        sda: int,
        scl: int,
        address: int = 0x68,
        target_hz: int = 20,
    ) -> None:
        """
        Initialize IMU sensor wrapper.

        Args:
            i2c (I2C): Configured MicroPython I2C bus
            address (int): I2C address of ICM20948 sensor
            target_hz (int): Desired polling frequency in Hz
        """
        i2c = I2C(0, sda=Pin(sda), scl=Pin(scl), freq=400000)

        self._sensor = icm20948.ICM20948(i2c, address=address)
        self._period_us: int = int(1_000_000 / target_hz)
        self._next_tick_us: int = time.ticks_us()

        # Bias offsets (in physical units: m/s² for accel, rad/s for gyro)
        self._acc_bias = (0.0, 0.0, 0.0)
        self._gyro_bias = (0.0, 0.0, 0.0)

    def configure(
        self,
        acc_range: int = icm20948.RANGE_4G,
        gyro_scale: int = icm20948.FS_500_DPS,
        acc_divisor: int = 22,
        gyro_divisor: int = 22,
    ) -> None:
        """
        Configure basic IMU ranges and sample-rate divisors.

        Note:
            divisor=22 gives ~48.9Hz (1125 / (1 + 22)).

        Args:
            acc_range (int): Accelerometer full scale constant
            gyro_scale (int): Gyroscope full scale constant
            acc_divisor (int): Accelerometer data rate divisor
            gyro_divisor (int): Gyroscope data rate divisor
        """
        self._sensor.accelerometer_range = acc_range
        self._sensor.gyro_full_scale = gyro_scale
        self._sensor.acc_data_rate_divisor = acc_divisor
        self._sensor.gyro_data_rate_divisor = gyro_divisor

    def set_bias(
        self,
        acc_bias: tuple[float, float, float] = (0.0, 0.0, 0.0),
        gyro_bias: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> None:
        """
        Set manual sensor bias corrections.

        Args:
            acc_bias (tuple[float, float, float]): (ax, ay, az) bias in m/s²
            gyro_bias (tuple[float, float, float]): (gx, gy, gz) bias in rad/s
        """
        self._acc_bias = acc_bias
        self._gyro_bias = gyro_bias

    def calibrate_gyro_bias(self, samples: int = 200, delay_us: int = 5000) -> tuple[float, float, float]:
        """
        Estimate gyroscope bias while sensor is perfectly still.

        Args:
            samples (int): Number of samples for averaging
            delay_us (int): Delay between reads in microseconds

        Returns:
            tuple[float, float, float]: Estimated (gx, gy, gz) bias in rad/s
        """
        sx = sy = sz = 0.0

        for _ in range(samples):
            gx, gy, gz = self._sensor.gyro
            sx += gx
            sy += gy
            sz += gz
            time.sleep_us(delay_us)

        bias = (sx / samples, sy / samples, sz / samples)
        self._gyro_bias = bias
        return bias

    def wait_next_tick(self) -> None:
        """
        Wait until the next target sampling instant.
        Use this method to keep a stable polling period in controller loops.
        """
        now = time.ticks_us()
        dt = time.ticks_diff(self._next_tick_us, now)
        if dt > 0:
            time.sleep_us(dt)

        self._next_tick_us = time.ticks_add(self._next_tick_us, self._period_us)

    def read_sample(self) -> IMUSample:
        """
        Read one IMU sample with timestamp and bias correction.

        Returns:
            IMUSample: Sensor data sample
        """
        ax, ay, az = self._sensor.acceleration
        _, _, gz = self._sensor.gyro

        return IMUSample(
            ax = ax - self._acc_bias[0],
            ay = ay - self._acc_bias[1],
            az = az - self._acc_bias[2],
            gz = gz - self._gyro_bias[2],
        )
