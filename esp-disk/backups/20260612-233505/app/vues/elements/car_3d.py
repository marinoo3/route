import math

from app.libs.micropython_ssd1306 import SSD1306_I2C

from app.vues.elements import DisplayElement

# Simple low-poly car mesh (centered near origin).
#   x: width (left/right)
#   y: height (up is negative, since screen Y grows downward)
#   z: length (front/back)
_VERTICES = [
    # body box
    [-0.6,  0.3, -1.1],   # 0
    [ 0.6,  0.3, -1.1],   # 1
    [ 0.6,  0.3,  1.1],   # 2
    [-0.6,  0.3,  1.1],   # 3
    [-0.6, -0.1, -1.1],   # 4
    [ 0.6, -0.1, -1.1],   # 5
    [ 0.6, -0.1,  1.1],   # 6
    [-0.6, -0.1,  1.1],   # 7
    # cabin top (shorter, set back)
    [-0.45, -0.5, -0.3],  # 8
    [ 0.45, -0.5, -0.3],  # 9
    [ 0.45, -0.5,  0.7],  # 10
    [-0.45, -0.5,  0.7],  # 11
]

_EDGES = [
    # body box
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
    # cabin top
    (8, 9), (9, 10), (10, 11), (11, 8),
    # cabin to body
    (8, 4), (9, 5), (10, 6), (11, 7),
]

# Wheel hub centers, at the four lower corners. Drawn as flat 2D circles.
_WHEELS = [
    [-0.6, 0.3, -0.75],
    [ 0.6, 0.3, -0.75],
    [-0.6, 0.3,  0.75],
    [ 0.6, 0.3,  0.75],
]


class Car3D(DisplayElement):
    """
    A simple low-poly 3D wireframe car that rotates a little each time it is drawn.
    """

    def __init__(self, *args, speed: float = 0.03, **kwargs) -> None:
        """
        Create a rotating car element.

        Args:
            speed (float): Angle advanced per draw (radians). Lower is slower.
            *args, **kwargs: Forwarded to DisplayElement.
        """
        super().__init__(*args, **kwargs)
        self.angle = 0.0
        self.speed = speed

    def _rotate(self, point: list, ax: float, ay: float) -> list:
        """
        Rotate a point around the X and Y axes.

        Args:
            point (list): [x, y, z] coordinates.
            ax (float): Rotation angle around X (radians).
            ay (float): Rotation angle around Y (radians).

        Returns:
            list: Rotated [x, y, z] coordinates.
        """
        x, y, z = point

        # rotate around X
        y, z = (
            y * math.cos(ax) - z * math.sin(ax),
            y * math.sin(ax) + z * math.cos(ax),
        )

        # rotate around Y
        x, z = (
            x * math.cos(ay) + z * math.sin(ay),
            -x * math.sin(ay) + z * math.cos(ay),
        )

        return [x, y, z]

    def _project(
            self,
            point: list,
            cx: int, cy: int, scale: float
    ) -> tuple:
        """
        Project a 3D point onto the 2D display.

        Args:
            point (list): [x, y, z] coordinates.
            cx (int): Center X on screen.
            cy (int): Center Y on screen.
            scale (float): Projection scale factor.

        Returns:
            tuple: (x, y) screen coordinates.
        """
        x, y, z = point
        distance = 4
        factor = scale / (z + distance)
        return (int(x * factor + cx), int(y * factor + cy))

    def _circle(self, oled: SSD1306_I2C, cx: int, cy: int, r: int, c: int = 1) -> None:
        """
        Draw a 2D outline circle using the midpoint algorithm.

        Args:
            oled (SSD1306_I2C): Oled display.
            cx (int): Circle center X.
            cy (int): Circle center Y.
            r (int): Radius in pixels.
            c (int): Pixel color.
        """
        x = r
        y = 0
        err = 1 - r
        while x >= y:
            oled.pixel(cx + x, cy + y, c)
            oled.pixel(cx + y, cy + x, c)
            oled.pixel(cx - y, cy + x, c)
            oled.pixel(cx - x, cy + y, c)
            oled.pixel(cx - x, cy - y, c)
            oled.pixel(cx - y, cy - x, c)
            oled.pixel(cx + y, cy - x, c)
            oled.pixel(cx + x, cy - y, c)
            y += 1
            if err < 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x) + 1

    def _default_renderer(
            self,
            oled: SSD1306_I2C,
            rx: int, ry: int, rw: int, rh: int,
            rvalue: dict
    ) -> None:
        """
        Render the rotating wireframe car and advance the rotation.

        Args:
            oled (SSD1306_I2C): Oled display
            rx (int): Position x
            ry (int): Position y
            rw (int): Width
            rh (int): Height
            rvalue (Any): Value to render
        """
        cx = rx + rw // 2
        cy = ry + rh // 2
        scale = min(rw, rh)

        projected = []
        for v in _VERTICES:
            r = self._rotate(v, self.angle, self.angle)
            projected.append(self._project(r, cx, cy, scale))

        for a, b in _EDGES:
            p1 = projected[a]
            p2 = projected[b]
            oled.line(p1[0], p1[1], p2[0], p2[1], 1)

        # Wheels: flat 2D circles at the projected hub positions.
        for hub in _WHEELS:
            r = self._rotate(hub, self.angle, self.angle)
            px, py = self._project(r, cx, cy, scale)
            radius = max(2, int(0.18 * scale / (r[2] + 4)))
            self._circle(oled, px, py, radius)

        self.angle += self.speed
