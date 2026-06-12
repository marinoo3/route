from machine import Pin, I2C
from micropython_icm20948 import icm20948
from micropython_ssd1306 import SSD1306_I2C

import utime

# One shared I2C bus is fine if addresses differ (OLED 0x3C, ICM 0x68/0x69)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

oled = SSD1306_I2C(128, 32, i2c)
imu = icm20948.ICM20948(i2c, address=0x68)

imu.accelerometer_range = icm20948.RANGE_2G
imu.acc_data_rate = 48.9

# -------- Timing / display ----------
dt_ms = 20
dt = dt_ms / 1000.0
trail_seconds = 4
max_points = int(trail_seconds * 1000 / dt_ms)

cx, cy = 64, 16
scale = 30.0

# -------- Motion state (world-ish in integrated sensor frame) ----------
vx = vy = 0.0
px = py = 0.0
trail_world = []

# -------- Gravity estimation ----------
# LPF: bigger alpha = slower gravity update (more motion passes through)
alpha_g = 0.98

# init gravity estimate while still
oled.fill(0)
oled.text("Keep still...", 0, 0)
oled.show()

sx = sy = sz = 0.0
N = 120
for _ in range(N):
    ax, ay, az = imu.acceleration
    sx += ax; sy += ay; sz += az
    utime.sleep_ms(10)

gx = sx / N
gy = sy / N
gz = sz / N

# -------- Drift controls ----------
acc_deadband = 0.15     # m/s^2 on linear accel
vel_damping = 0.995
stationary_thr = 0.25   # m/s^2 magnitude threshold for "not moving"

while True:
    ax, ay, az = imu.acceleration

    # Update gravity estimate (low-pass accel)
    gx = alpha_g * gx + (1.0 - alpha_g) * ax
    gy = alpha_g * gy + (1.0 - alpha_g) * ay
    gz = alpha_g * gz + (1.0 - alpha_g) * az

    # Linear acceleration (motion only approx)
    lax = ax - gx
    lay = ay - gy
    laz = az - gz

    # deadband
    if -acc_deadband < lax < acc_deadband: lax = 0.0
    if -acc_deadband < lay < acc_deadband: lay = 0.0

    # integrate only XY (screen plane)
    vx += lax * dt
    vy += lay * dt

    # stationary detection -> zero velocity update
    amag = math.sqrt(lax*lax + lay*lay + laz*laz)
    if amag < stationary_thr:
        vx *= 0.5
        vy *= 0.5
        if abs(vx) < 0.01: vx = 0.0
        if abs(vy) < 0.01: vy = 0.0

    # damping
    vx *= vel_damping
    vy *= vel_damping

    px += vx * dt
    py += vy * dt

    trail_world.append((px, py))
    if len(trail_world) > max_points:
        trail_world.pop(0)

    # Draw relative to current point => current point stays centered
    oled.fill(0)
    prev = None
    for wx, wy in trail_world:
        sx = int(cx + (wx - px) * scale)
        sy = int(cy - (wy - py) * scale)
        if 0 <= sx <= 127 and 0 <= sy <= 31:
            if prev is not None:
                oled.line(prev[0], prev[1], sx, sy, 1)
            prev = (sx, sy)
        else:
            prev = None

    # center marker
    oled.pixel(cx, cy, 1)
    oled.show()

    utime.sleep_ms(dt_ms)