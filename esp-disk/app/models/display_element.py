

class DisplayElement:
    """
    One drawable UI element with a fixed maximum bounding box.
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        width: int,
        height: int,
        renderer,
        value= None,
        visible: bool = True,
        z_index: int = 0,
    ) -> None:
        """
        Create a display element.

        Args:
            name (str): Unique element name.
            x (int): Top-left X position.
            y (int): Top-left Y position.
            width (int): Maximum element width.
            height (int): Maximum element height.
            renderer: Callable with signature
                renderer(oled, x, y, width, height, value) -> None
            value: Initial value passed to renderer.
            visible (bool): True if element is visible.
            z_index (int): Drawing order (lower first, higher on top).

        Returns:
            None
        """
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.renderer = renderer
        self.value = value
        self.visible = visible
        self.z_index = z_index
        self.dirty = True

    def bbox(self) -> tuple:
        """
        Return current bounding box.

        Args:
            None

        Returns:
            tuple: (x, y, width, height)
        """
        return (self.x, self.y, self.width, self.height)

    def draw(self, oled) -> None:
        """
        Draw the element using its renderer callback.

        Args:
            oled: SSD1306 instance.

        Returns:
            None
        """
        if self.visible:
            self.renderer(oled, self.x, self.y, self.width, self.height, self.value)