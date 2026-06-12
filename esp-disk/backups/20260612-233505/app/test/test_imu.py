import time
from machine import Pin, I2C
from micropython_icm20948 import icm20948

# Correct ESP32 I2C setup
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
# Initialize IMU
icm = icm20948.ICM20948(i2c, address=0x68)


while True:
    accx, accy, accz = icm.acceleration
    gyrox, gyroy, gyroz = icm.gyro
    print(f"x: {accx}m/s², y: {accy},m/s² z: {accz}m/s²")
    print(f"x: {gyrox}°/s, y: {gyroy}°/s, z: {gyroz}°/s")
    print()
    time.sleep(1)