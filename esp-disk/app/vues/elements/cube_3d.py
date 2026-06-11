import math

from app.libs.micropython_ssd1306 import SSD1306_I2C

from app.vues.elements import DisplayElement

# Cube vertices (centered at origin)
_VERTICES = [
    [-1, -1, -1],
    [ 1, -1, -1],
    [ 1,  1, -1],
    [-1,  1, -1],
    [-1, -1,  1],
    [ 1, -1,  1],
    [ 1,  1,  1],
    [-1,  1,  1],
]

# Edges (pairs of vertex indices)
_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]


class Cube3D(DisplayElement):
    """
    A 3D wireframe cube that rotates a little each time it is drawn.
    """

    def __init__(self, *args, speed: float = 0.1, **kwargs) -> None:
        """
        Create a rotating cube element.

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
            cx: int, cy: int, scale: int
    ) -> tuple:
        """
        Project a 3D point onto the 2D display.

        Args:
            point (list): [x, y, z] coordinates.
            cx (int): Center X on screen.
            cy (int): Center Y on screen.
            scale (int): Projection scale factor.

        Returns:
            tuple: (x, y) screen coordinates.
        """
        x, y, z = point
        distance = 3
        factor = scale / (z + distance)
        return (int(x * factor + cx), int(y * factor + cy))

    def _default_renderer(
            self,
            oled: SSD1306_I2C,
            rx: int, ry: int, rw: int, rh: int,
            rvalue: dict
    ) -> None:
        """
        Render the rotating wireframe cube and advance the rotation.

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
        scale = min(rw, rh) * 3 // 4

        projected = []
        for v in _VERTICES:
            r = self._rotate(v, self.angle, self.angle)
            projected.append(self._project(r, cx, cy, scale))

        for a, b in _EDGES:
            p1 = projected[a]
            p2 = projected[b]
            oled.line(p1[0], p1[1], p2[0], p2[1], 1)

        self.angle += self.speed
