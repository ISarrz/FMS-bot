from typing import List

from PIL import Image, ImageDraw, ImageFont
from modules.data_updater.painter.pixels import Pixels
from modules.data_updater.painter.base_container import BaseContainer
from modules.data_updater.painter.container import Container
from modules.data_updater.painter.text import Text


class Column(BaseContainer):
    pixels: Pixels
    _content: List
    _outline_size: int = 1
    _cell_width: int = 0
    _cell_height: int = 0
    _cell_vertical_alignment = "center"
    _cell_horizontal_alignment = "center"
    _cell_space=0
    _height: int=0

    def _changed(self, field):
        if field == "left_top":
            self._update_pixels()

    def __init__(self, left_top=(0, 0), outline_size=1):
        self.pixels = Pixels(container=self)
        self._content = []
        self._outline_size = outline_size
        self.pixels.left_top = left_top

    def add(self, content: BaseContainer):
        new_cell = Container()
        new_cell.content = content
        new_cell._outline_size = self._outline_size
        new_cell.pixels.padding = self.pixels.padding
        new_cell.vertical_alignment = self._cell_vertical_alignment
        new_cell.horizontal_alignment = self._cell_horizontal_alignment
        self._content.append(new_cell)
        self._update_pixels()

    def _update_pixels(self):
        self._height = len(self._content)
        self._cell_width = 0
        self._cell_height = 0
        for cell in self._content:
            self._cell_width = max(self._cell_width, cell.pixels.width)
            self._cell_height = max(self._cell_height, cell.pixels.height)

        self.pixels.width = self._cell_width
        self.pixels.height = self._cell_height * self._height

        current_point = self.pixels.left_top
        for cell in self._content:
            cell.pixels.width = self._cell_width
            cell.pixels.height = self._cell_height

            cell.pixels.left_top = current_point
            current_point = (cell.pixels.left_x, cell.pixels.bottom_y + self._cell_space)

    def draw(self, canvas):
        for cell in self._content:
            cell.draw(canvas)


if __name__ == "__main__":
    column = Column(left_top=(10, 10), outline_size=1)
    text1 = Text(value="Hello, world!")
    text2 = Text(value="Hello!")
    text1.size = 30
    text2.size = 12
    column.add(text1)
    column.add(text2)
    column.outline_size = 0

    image = Image.new("RGB", (300, 100), color="white")
    canvas = ImageDraw.Draw(image)
    column.draw(canvas)

    image.save("text_image.png")
    image.show()
