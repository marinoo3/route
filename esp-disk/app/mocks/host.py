"""
host.py - host test entry point for esp-disk.

Run this INSTEAD of main.py to exercise the app on the macOS unix micropython
port with ESP-only drivers swapped for host mocks:

    micropython app/mocks/host.py        (from the repo root)

It pre-registers host mocks in sys.modules under the real drivers'
fully-qualified `app.libs.*` names, so the hardcoded imports inside the
application resolve to the mocks here -- without modifying any non-mock code:

  * app.libs.micropython_icm20948.icm20948  -> app/mocks/icm20948_mock.py
    (so app/modules/imu_sensor.py gets a fake sensor)
  * app.libs.micropython_ssd1306            -> app/mocks/micropython_ssd1306/
    (so the OLED driver renders to the TERMINAL instead of pushing pixels over
    a mock I2C bus that discards them -- which is why main.py shows nothing)

On the ESP nothing imports this file, so the real drivers are used there.
"""

import sys

# Running a script file puts sys.path[0] at the script's dir (app/mocks), not
# the repo root, so `import app` would fail.  Put the cwd (repo root - run from
# there) on the path first.
if "" not in sys.path:
    sys.path.insert(0, "")

from app.mocks import icm20948_mock
from app.mocks import micropython_ssd1306 as ssd1306_mock

# --- swap the ICM20948 driver ----------------------------------------------
# Setting the full dotted name (and a tiny package stand-in exposing it as an
# attribute) means the real app/libs/micropython_icm20948 package is never
# loaded.
_ICM_PKG = "app.libs.micropython_icm20948"

sys.modules[_ICM_PKG + ".icm20948"] = icm20948_mock


class _IcmPkg:
    icm20948 = icm20948_mock


sys.modules[_ICM_PKG] = _IcmPkg

# --- swap the SSD1306 OLED driver for the terminal renderer ----------------
# Every `from app.libs.micropython_ssd1306 import SSD1306_I2C` then yields the
# terminal mock, so the display shows up in the console on the host.
sys.modules["app.libs.micropython_ssd1306"] = ssd1306_mock


# Import and run the real application.  main.py only auto-runs under
# `__name__ == "__main__"`, so we drive its main() coroutine ourselves.
import uasyncio as asyncio  # noqa: E402
import main  # noqa: E402

if __name__ == "__main__":
    try:
        asyncio.run(main.main())
    except KeyboardInterrupt:
        print("Exit")
