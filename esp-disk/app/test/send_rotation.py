# main.py (MicroPython on ESP32)
import time
import math
from machine import Pin, I2C
from micropython_icm20948 import icm20948

# I2C setup for ESP32
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
icm = icm20948.ICM20948(i2c, address=0x68)

# Optional sensor config (uncomment if supported by your driver build)
try:
    icm.clock_select = icm20948.CLK_SELECT_BEST
    icm.accelerometer_range = icm20948.RANGE_2G
    icm.gyro_full_scale = icm20948.FS_500_DPS
    icm.acc_dlpf_cutoff = icm20948.FREQ_50_4
    icm.gyro_dlpf_cutoff = icm20948.G_FREQ_51_2
except Exception:
    pass

# Complementary filter params
alpha = 0.98
roll = 0.0
pitch = 0.0
yaw = 0.0

# --- Gyro bias calibration (keep sensor still) ---
print("Calibrating gyro... keep sensor still")
n = 300
bx = by = bz = 0.0
for _ in range(n):
    gx, gy, gz = icm.gyro
    bx += gx
    by += gy
    bz += gz
    time.sleep_ms(5)

bx /= n
by /= n
bz /= n
print("Gyro bias:", bx, by, bz)

last_us = time.ticks_us()

while True:
    accx, accy, accz = icm.acceleration      # m/s²
    gx, gy, gz = icm.gyro                    # deg/s

    # Remove gyro bias
    gx -= bx
    gy -= by
    gz -= bz

    now_us = time.ticks_us()
    dt = time.ticks_diff(now_us, last_us) / 1_000_000.0
    last_us = now_us

    # Accel-based roll/pitch (in degrees)
    acc_roll = math.degrees(math.atan2(accy, accz))
    acc_pitch = math.degrees(math.atan2(-accx, math.sqrt(accy * accy + accz * accz)))

    # Gyro integration
    roll += gx * dt
    pitch += gy * dt
    yaw += gz * dt  # no magnetometer correction -> may drift

    # Complementary fusion
    roll = alpha * roll + (1.0 - alpha) * acc_roll
    pitch = alpha * pitch + (1.0 - alpha) * acc_pitch

    # Send CSV line
    # Format: roll,pitch,yaw
    print("{:.2f},{:.2f},{:.2f}".format(roll, pitch, yaw))

    time.sleep_ms(10)  # ~100 Hz

