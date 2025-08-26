from typing import List

from modules.data_updater.painter.pixels import Pixels
from modules.data_updater.painter.text import Text
from modules.data_updater.painter.base_container import BaseContainer


class Container(BaseContainer):
    pixels: Pixels
    _outline_size: int = 0
    _outline_color: str = "black"
    _fill: str
    _content: None | BaseContainer = None
    _radius: int = 0
    _vertical_alignment = "top"
    _horizontal_alignment = "left"
    _left_outline_color: str = "black"
    _right_outline_color: str = "black"
    _top_outline_color: str = "black"
    _bottom_outline_color: str = "black"

    @property
    def outline_color(self):
        return self._outline_color

    @outline_color.setter
    def outline_color(self, value):
        self._outline_color = value
        self.top_outline_color = value
        self.bottom_outline_color = value
        self.left_outline_color = value
        self.right_outline_color = value

    @property
    def left_outline_color(self):
        return self._left_outline_color

    @left_outline_color.setter
    def left_outline_color(self, value):
        self._left_outline_color = value

    @property
    def right_outline_color(self):
        return self._right_outline_color

    @right_outline_color.setter
    def right_outline_color(self, value):
        self._right_outline_color = value

    @property
    def top_outline_color(self):
        return self._top_outline_color

    @top_outline_color.setter
    def top_outline_color(self, value):
        self._top_outline_color = value

    @property
    def bottom_outline_color(self):
        return self._bottom_outline_color

    @bottom_outline_color.setter
    def bottom_outline_color(self, value):
        self._bottom_outline_color = value

    @property
    def fill(self):
        return self._fill

    @fill.setter
    def fill(self, value):
        self._fill = value

    @property
    def outline_size(self) -> int:
        return self._outline_size

    @outline_size.setter
    def outline_size(self, value):
        self._outline_size = value

    def __init__(self, fill=None, left_top=(0, 0), radius=0):
        self._fill = fill
        self.pixels = Pixels(container=self)
        self.pixels.left_top = left_top
        self._radius = radius
        self._update_pixels()

    @property
    def vertical_alignment(self):
        return self._vertical_alignment

    @vertical_alignment.setter
    def vertical_alignment(self, value):
        self._vertical_alignment = value
        self._update_pixels()

    @property
    def horizontal_alignment(self):
        return self._horizontal_alignment

    @horizontal_alignment.setter
    def horizontal_alignment(self, value):
        self._horizontal_alignment = value
        self._update_pixels()

    def draw(self, canvas):
        cords = (self.pixels.left_x, self.pixels.top_y, self.pixels.right_x, self.pixels.bottom_y)
        canvas.rectangle(cords,
                         fill=self._fill,
                         outline=None,
                         width=0)

        left_x = self.pixels.left_x
        right_x = self.pixels.right_x
        top_y = self.pixels.top_y
        bottom_y = self.pixels.bottom_y
        gap1 = (self.outline_size - 1) // 2
        gap2 = (self.outline_size) // 2

        left_top = (left_x, top_y)
        right_top = (right_x, top_y)
        left_bottom = (left_x, bottom_y)
        right_bottom = (right_x, bottom_y)
        if self.outline_size:
            canvas.line((left_x - gap1, top_y, right_x + gap2, top_y), fill=self.top_outline_color,
                        width=self._outline_size)
            canvas.line((left_x, top_y - gap1, left_x, bottom_y + gap2), fill=self.left_outline_color,
                        width=self._outline_size)
            canvas.line((left_x - gap1, bottom_y, right_x + gap2, bottom_y), fill=self.bottom_outline_color,
                        width=self._outline_size)
            canvas.line((right_x, top_y - gap1, right_x, bottom_y + gap2), fill=self.right_outline_color,
                        width=self._outline_size)
        if self._content:
            self._content.draw(canvas)

    def _changed(self, field):
        if field == "padding":
            self._update_pixels()
        if field == "left_top":
            self._update_pixels()

    def _update_pixels(self):
        self._update_width()
        self._update_height()
        self._update_content()

    def _update_width(self):
        self.pixels.width = max(self.pixels.width, 2 * self.pixels.padding)
        if self.content:
            self.pixels.width = max(self.pixels.width,
                                    self.content.pixels.width + 2 * self.pixels.padding + self.content.pixels.margin * 2
                                    )

    def _update_height(self):
        self.pixels.height = max(self.pixels.height, 2 * self.pixels.padding)
        if self.content:
            self.pixels.height = max(self.pixels.height,
                                     self.content.pixels.height + 2 * self.pixels.padding + self.content.pixels.margin * 2
                                     )

    def squeeze(self):
        self.pixels.height = 0
        self.pixels.width = 0
        self._update_pixels()

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
            self._content.pixels.left_top = self.pixels.left_x, self.pixels.top_y + self.pixels.padding + self.content.pixels.margin

        if self._horizontal_alignment == "left":
            self._content.pixels.left_top = self.pixels.left_x + self.pixels.padding + self.content.pixels.margin, self.pixels.top_y

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
    # text = Text(value="Hello, world!", left_top=(10, 10))
    # text2 = Text(value="Hello, world!", left_top=(10, 10))
    container = Container(left_top=(10, 10), fill=None, radius=0)
    container._outline_size = 0
    container._outline_color = "blue"
    # container.content = text
    # container.pixels.padding = 5
    container.pixels.width = 100
    container.pixels.height = 50
    #
    container2 = Container(left_top=(container.pixels.right_x, container.pixels.top_y), fill=None, radius=0)
    container2.outline_size = 2
    container2.outline_color = "red"
    container2.left_outline_color = "black"
    container2.pixels.width = 100
    container2.pixels.height = 50
    # container2.content = text2
    # container2.pixels.padding = 5
    #
    canvas = ImageDraw.Draw(image)
    # container.draw(canvas)
    container2.draw(canvas)

    image.save("text_image.png")
    image.show()
