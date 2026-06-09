from app.libs.micropython_ssd1306 import SSD1306_I2C
from machine import Pin, I2C
import math
import time

# Initialisation I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(128, 32, i2c)
oled.fill(1)
oled.show()

# Cube vertices (centered at origin)
vertices = [
    [-1, -1, -1],
    [ 1, -1, -1],
    [ 1,  1, -1],
    [-1,  1, -1],
    [-1, -1,  1],
    [ 1, -1,  1],
    [ 1,  1,  1],
    [-1,  1,  1]
]

# Edges (pairs of vertex indices)
edges = [
    (0,1),(1,2),(2,3),(3,0),
    (4,5),(5,6),(6,7),(7,4),
    (0,4),(1,5),(2,6),(3,7)
]

def rotate(point, ax, ay):
    x, y, z = point

    # rotate around X
    y, z = (
        y * math.cos(ax) - z * math.sin(ax),
        y * math.sin(ax) + z * math.cos(ax)
    )

    # rotate around Y
    x, z = (
        x * math.cos(ay) + z * math.sin(ay),
        -x * math.sin(ay) + z * math.cos(ay)
    )

    return [x, y, z]

def project(point):
    x, y, z = point
    distance = 3
    factor = 24 / (z + distance)
    x = int(x * factor + 64)
    y = int(y * factor + 16)
    return (x, y)

angle = 0

while True:
    oled.fill(0)

    projected = []

    for v in vertices:
        r = rotate(v, angle, angle)
        p = project(r)
        projected.append(p)

    # draw edges
    for e in edges:
        p1 = projected[e[0]]
        p2 = projected[e[1]]
        oled.line(p1[0], p1[1], p2[0], p2[1], 1)

    oled.show()

    angle += 0.1
    time.sleep(0.05)

