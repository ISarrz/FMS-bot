from typing import List

from modules.data_updater.painter.pixels import Pixels
from modules.data_updater.painter.text import Text
from modules.data_updater.painter.base_container import BaseContainer


class Container:
    pixels: Pixels
    _outline_size: int = 0
    _outline_color: str = "black"
    _fill: str
    _content: None | BaseContainer = None
    _radius: int = 0
    _vertical_alignment = "top"
    _horizontal_alignment = "left"

    def __init__(self, fill="white", left_top=(0, 0), radius=0):
        self._fill = fill
        self.pixels = Pixels()
        self.pixels.left_top = left_top
        self._radius = radius
        self._update_pixels()

    def draw(self, canvas):
        cords = (self.pixels.left_x, self.pixels.top_y, self.pixels.right_x, self.pixels.bottom_y)
        canvas.rounded_rectangle(cords,
                                 radius=self._radius,
                                 fill=self._fill,
                                 outline=self._outline_color,
                                 width=self._outline_size)
        if self._content:
            self._content.draw(canvas)

    @property
    def left_top(self):
        return self.pixels.left_top

    @left_top.setter
    def left_top(self, value):
        self.pixels.left_top = value
        self._update_pixels()

    def _update_pixels(self):
        self._update_width()
        self._update_height()
        self._update_content()

    def _update_width(self):
        self.pixels.width = max(self.pixels.width, 2 * self.pixels.padding)
        if self.content:
            self.pixels.width = max(self.pixels.width, self.content.pixels.width + 2 * self.pixels.padding)

    def _update_height(self):
        self.pixels.height = max(self.pixels.height, 2 * self.pixels.padding)
        if self.content:
            self.pixels.height = max(self.pixels.height, self.content.pixels.height + 2 * self.pixels.padding)

    @property
    def vertical_alignment(self):
        return self._vertical_alignment

    @property
    def horizontal_alignment(self):
        return self._horizontal_alignment

    @vertical_alignment.setter
    def vertical_alignment(self, value):
        self._vertical_alignment = value
        self._update_pixels()

    @horizontal_alignment.setter
    def horizontal_alignment(self, value):
        self._horizontal_alignment = value
        self._update_pixels()

    def _update_content(self):
        if not self.content:
            return

        if self._vertical_alignment == "top":
            self._content.pixels.left_top = self.pixels.left_x, self.pixels.top_y + self.pixels.padding

        if self._horizontal_alignment == "left":
            self._content.pixels.left_top = self.pixels.left_x + self.pixels.padding, self.pixels.top_y

        if self._horizontal_alignment == "center":
            center_x = self.pixels.center[0]
            self._content.pixels.center = center_x, self._content.pixels.center[1]

        if self._vertical_alignment == "center":
            center_y = self.pixels.center[1]
            self._content.pixels.center = self._content.pixels.center[0], center_y

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value: BaseContainer):
        self._content = value
        self._update_pixels()


if __name__ == "__main__":
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (300, 200), color="white")
    text = Text(value="Hello, world!", left_top=(10, 10))
    text.size = 50
    container = Container(left_top=(10, 10), fill="gray", radius=0)
    # container.pixels.width = 50
    # container.pixels.height = 50
    container.pixels.padding = 0
    container.content = text

    canvas = ImageDraw.Draw(image)
    container.draw(canvas)
    image.save("text_image.png")
    image.show()
