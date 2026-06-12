"""
icm20948_mock.py - host stand-in for app/libs/micropython_icm20948/icm20948.py.

This replaces the *whole* ICM20948 driver (not just the I2C bytes) so host tests
don't depend on the real register-level driver.  It is injected into sys.modules
under the name `app.libs.micropython_icm20948.icm20948` by app/mocks/host.py, so
`from app.libs.micropython_icm20948 import icm20948` resolves here on the host
while the real lib is used unchanged on the ESP.

Only the surface the application touches is implemented: the ICM20948 class
(constructor + acceleration/gyro properties + the four config attributes) and the
RANGE_* / FS_*_DPS constants referenced by app/modules/imu_sensor.py.
"""

import math
import time

# -- Accelerometer full-scale ranges (values mirror the real driver) ---------
RANGE_2G = 0b00
RANGE_4G = 0b01
RANGE_8G = 0b10
RANGE_16G = 0b11

# -- Gyroscope full-scale ranges --------------------------------------------
FS_250_DPS = 0b00
FS_500_DPS = 0b01
FS_1000_DPS = 0b10
FS_2000_DPS = 0b11


class ICM20948:
    """Host emulation that returns gently moving, physically plausible data."""

    def __init__(self, i2c=None, address=0x69):
        self._i2c = i2c
        self._address = address

        # Config attributes the app sets; stored but otherwise inert.
        self.accelerometer_range = RANGE_4G
        self.gyro_full_scale = FS_500_DPS
        self.acc_data_rate_divisor = 22
        self.gyro_data_rate_divisor = 22

        self._t0 = time.ticks_ms()

    def _elapsed(self):
        return time.ticks_diff(time.ticks_ms(), self._t0) / 1000.0

    @property
    def acceleration(self):
        """(ax, ay, az) in m/s^2 - ~1 g on Z with a small wobble."""
        t = self._elapsed()
        ax = 2.0 * math.sin(t)
        ay = 2.0 * math.cos(t)
        az = 9.80665 + 0.5 * math.sin(t * 1.7)
        return (ax, ay, az)

    @property
    def gyro(self):
        """(gx, gy, gz) in rad/s - small oscillation, matches real driver units."""
        t = self._elapsed()
        gx = 0.5 * math.sin(t * 1.3)
        gy = 0.5 * math.cos(t * 0.9)
        gz = 0.7 * math.sin(t * 0.5)
        return (gx, gy, gz)
