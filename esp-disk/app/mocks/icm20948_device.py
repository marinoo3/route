"""
icm20948_device.py - host emulation of the ICM20948 IMU at the register level.

The real driver (app/libs/micropython_icm20948) talks to the sensor purely
through I2C readfrom_mem / writeto_mem, switching register banks via REG_BANK_SEL
(0x7F).  This emulator keeps a per-bank register map, answers the WHO_AM_I probe
with 0xEA so the driver initialises, and synthesises gently moving accelerometer
and gyroscope data so the rest of the program receives realistic samples.

It is auto-registered onto the mock machine.I2C bus (see machine.py) at the
ICM20948 addresses, so no application code needs to change.
"""

import math
import struct
import time

# Register map (bank 0 unless noted)
_REG_BANK_SEL = 0x7F
_WHO_AM_I = 0x00       # bank 0, returns 0xEA
_ACCEL_XOUT_H = 0x2D   # bank 0, 6 bytes (>hhh)
_GYRO_XOUT_H = 0x33    # bank 0, 6 bytes (>hhh)
_TEMP_OUT = 0x3A       # bank 0

_DEVICE_ID = 0xEA

# Matches RANGE_4G sensitivity / FS_500_DPS sensitivity used by the app so the
# synthesised raw counts map to sensible physical units.
_ACC_1G_RAW = 8192     # 1 g at the 4 g range
_GYRO_RAW_SPAN = 4000  # ~modest rotation rate


class ICM20948Device:
    def __init__(self):
        # One register map per user bank (0..3).
        self._banks = {0: {}, 1: {}, 2: {}, 3: {}}
        self._bank = 0
        self._t0 = time.ticks_ms()

    # -- bank handling -------------------------------------------------------
    def _current_bank(self):
        return self._bank

    # -- synthesised motion --------------------------------------------------
    def _phase(self):
        return time.ticks_diff(time.ticks_ms(), self._t0) / 1000.0

    def _accel_bytes(self):
        t = self._phase()
        ax = int(1800 * math.sin(t))
        ay = int(1800 * math.cos(t))
        az = _ACC_1G_RAW + int(400 * math.sin(t * 1.7))
        return struct.pack(">hhh", _clamp(ax), _clamp(ay), _clamp(az))

    def _gyro_bytes(self):
        t = self._phase()
        gx = int(_GYRO_RAW_SPAN * math.sin(t * 1.3))
        gy = int(_GYRO_RAW_SPAN * math.cos(t * 0.9))
        gz = int(_GYRO_RAW_SPAN * math.sin(t * 0.5))
        return struct.pack(">hhh", _clamp(gx), _clamp(gy), _clamp(gz))

    # -- I2C device protocol (called by mock machine.I2C) -------------------
    def readfrom_mem(self, memaddr, nbytes, addrsize=8):
        bank = self._current_bank()

        if bank == 0 and memaddr == _WHO_AM_I:
            return _fit(bytes([_DEVICE_ID]), nbytes)

        if bank == 0 and memaddr == _ACCEL_XOUT_H:
            return _fit(self._accel_bytes(), nbytes)

        if bank == 0 and memaddr == _GYRO_XOUT_H:
            return _fit(self._gyro_bytes(), nbytes)

        # Fall back to whatever was last written to this register, else zeros.
        regs = self._banks[bank]
        out = bytearray()
        for i in range(nbytes):
            out.append(regs.get(memaddr + i, 0) & 0xFF)
        return bytes(out)

    def writeto_mem(self, memaddr, data, addrsize=8):
        data = bytes(data)

        if memaddr == _REG_BANK_SEL:
            # Bank lives in bits 4-5 of the value, mirrored in every bank.
            self._bank = (data[0] >> 4) & 0x03
            for regs in self._banks.values():
                regs[_REG_BANK_SEL] = data[0]
            return

        regs = self._banks[self._current_bank()]
        for i, byte in enumerate(data):
            regs[memaddr + i] = byte

    # Some I2C helpers use plain writeto/readfrom; keep them tolerant.
    def writeto(self, data):
        pass

    def readfrom(self, nbytes):
        return bytes(nbytes)


def _fit(payload, nbytes):
    """Truncate or zero-pad payload to exactly nbytes (no bytes.ljust on mpy)."""
    if len(payload) >= nbytes:
        return payload[:nbytes]
    return payload + bytes(nbytes - len(payload))


def _clamp(value):
    if value > 32767:
        return 32767
    if value < -32768:
        return -32768
    return value
