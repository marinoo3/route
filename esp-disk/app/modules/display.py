from app.mocks.micropython_ssd1306 import SSD1306_I2C
from app.vues.elements import DisplayElement

from machine import Pin, I2C


class Display:
    """
    Display manager for SSD1306.

    Notes:
        - Keeps UI elements by name.
        - Supports dirty-rectangle updates in RAM buffer.
        - Calls oled.show() once per render().
        - The provided SSD1306 driver still transfers full buffer on show().
    """

    def __init__(
            self,
            sda: int, 
            scl: int,
            background_color: int = 0
        ) -> None:
        """
        Initialize display manager.

        Args:
            oled: SSD1306_I2C or SSD1306_SPI instance.
            background_color (int): 0 (black) or 1 (white).
        """
        i2c = I2C(0, scl=Pin(scl), sda=Pin(sda))
        oled = SSD1306_I2C(128, 32, i2c)

        self._oled = oled
        self._bg = 1 if background_color else 0
        self._elements: dict[str, DisplayElement] = {}
        self._dirty_rects: list[tuple] = []
        self._full_dirty = True

    def draw_buf(self, buf):
            h = len(buf)
            w = len(buf[0])

            for y in range(h):
                if y >= self._oled.height:
                    break
                for x in range(w):
                    if x >= self._oled.width:
                        break
                    self._oled.pixel(x, y, buf[y][x])

    def add_element(
        self,
        name: str,
        element: DisplayElement
    ) -> None:
        """
        Register a new drawable element.

        Args:
            name (str): Unique element name.
            element (DisplayElement): Element to add to display
        """
        if name in self._elements:
            raise ValueError("Element already exists: {}".format(name))

        self._elements[name] = element
        self._mark_dirty_rect(element.bbox())

    def remove_element(self, name: str) -> None:
        """
        Remove an element and clear its area.

        Args:
            name (str): Element name.
        """
        element = self._require_element(name)
        self._mark_dirty_rect(element.bbox())
        del self._elements[name]

    def remove_all_elements(self) -> None:
        """
        Remove all elements from display
        """
        for element in self._elements.keys():
            self.remove_element(element)

    def set_value(self, name: str, value) -> None:
        """
        Update element value.

        Args:
            name (str): Element name.
            value: New value sent to renderer.
        """
        element = self._require_element(name)
        if element.value != value:
            element.value = value
            element.dirty = True
            self._mark_dirty_rect(element.bbox())

    def move_element(self, name: str, x: int, y: int) -> None:
        """
        Move an element to a new position.

        Args:
            name (str): Element name.
            x (int): New X.
            y (int): New Y.
        """
        element = self._require_element(name)
        old_bbox = element.bbox()

        if element.x != x or element.y != y:
            element.x = x
            element.y = y
            element.dirty = True
            self._mark_dirty_rect(old_bbox)
            self._mark_dirty_rect(element.bbox())

    def set_visible(self, name: str, visible: bool) -> None:
        """
        Show or hide an element.

        Args:
            name (str): Element name.
            visible (bool): Visibility state.
        """
        element = self._require_element(name)
        if element.visible != visible:
            element.visible = visible
            element.dirty = True
            self._mark_dirty_rect(element.bbox())    

    def clear(self) -> None:
        """
        Force full-screen clear and full redraw on next render().
        """
        self._full_dirty = True

    def render(self, force_full: bool = False) -> None:
        """
        Render one frame and push it to the display.

        Args:
            force_full (bool): If True, redraw full screen.
        """
        if force_full or self._full_dirty:
            self._oled.fill(self._bg)
            for element in self._sorted_elements():
                element.draw(self._oled)
                element.dirty = False
            self._dirty_rects = []
            self._full_dirty = False
            self._oled.show()
            return

        if not self._dirty_rects:
            # Nothing changed.
            return

        # 1) Clear dirty regions.
        rects = self._dirty_rects
        for rect in rects:
            x, y, w, h = rect
            self._oled.fill_rect(x, y, w, h, self._bg)

        # 2) Redraw any visible element intersecting dirty regions
        #    (handles overlaps), plus explicitly dirty ones.
        for element in self._sorted_elements():
            if not element.visible:
                element.dirty = False
                continue

            must_draw = element.dirty
            if not must_draw:
                eb = element.bbox()
                for rect in rects:
                    if self._intersects(eb, rect):
                        must_draw = True
                        break

            if must_draw:
                element.draw(self._oled)

            element.dirty = False

        self._dirty_rects = []
        self._oled.show()

    def add_text(
        self,
        name: str,
        x: int = 0,
        y: int = 0,
        max_chars: int = 16,
        template: str = "{}",
        value: str = "",
        visible: bool = True,
        z_index: int = 0,
    ) -> None:
        """
        Convenience helper for fixed-area text elements.

        Args:
            name (str): Unique element name.
            x (int): Text X position.
            y (int): Text Y position.
            max_chars (int): Maximum text length (8px per char).
            template (str): Format template, e.g. "T:{}C".
            value: Initial value.
            visible (bool): Initial visibility.
            z_index (int): Drawing order.
        """
        width = max_chars * 8
        height = 8

        def _text_renderer(
                oled: SSD1306_I2C, 
                rx: int, ry: int, rw: int, rh: int, 
                rvalue: str
            ):
            text = template.format(rvalue)
            oled.text(text, rx, ry, 1)

        self.add_element(
            name,
            DisplayElement(
                name=name,
                x=x,
                y=y,
                width=width,
                height=height,
                renderer=_text_renderer,
                value=value,
                visible=visible,
                z_index=z_index,
            )
        )

    def _require_element(self, name: str) -> DisplayElement:
        """
        Return element by name, raise KeyError if missing.

        Args:
            name (str): Element name.

        Returns:
            DisplayElement: Requested element.
        """
        if name not in self._elements:
            raise KeyError("Unknown element: {}".format(name))
        return self._elements[name]

    def _sorted_elements(self) -> list[DisplayElement]:
        """
        Return elements sorted by z_index.

        Returns:
            list: Sorted DisplayElement list.
        """
        return sorted(self._elements.values(), key=lambda e: e.z_index)

    def _mark_dirty_rect(self, rect: tuple) -> None:
        """
        Add clipped dirty rectangle.

        Args:
            rect (tuple): (x, y, width, height)

        Returns:
            None
        """
        clipped = self._clip_rect(rect)
        if clipped is not None:
            self._dirty_rects.append(clipped)

    def _clip_rect(self, rect: tuple):
        """
        Clip rectangle to screen bounds.

        Args:
            rect (tuple): (x, y, width, height)

        Returns:
            tuple | None: Clipped rect or None if outside.
        """
        x, y, w, h = rect
        if w <= 0 or h <= 0:
            return None

        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self._oled.width, x + w)
        y1 = min(self._oled.height, y + h)

        if x1 <= x0 or y1 <= y0:
            return None

        return (x0, y0, x1 - x0, y1 - y0)

    def _intersects(self, a: tuple, b: tuple) -> bool:
        """
        Check rectangle intersection.

        Args:
            a (tuple): Rect A (x, y, w, h)
            b (tuple): Rect B (x, y, w, h)

        Returns:
            bool: True if intersects.
        """
        ax, ay, aw, ah = a
        bx, by, bw, bh = b

        return not (
            ax + aw <= bx or
            bx + bw <= ax or
            ay + ah <= by or
            by + bh <= ay
        )