from __future__ import annotations
from typing import List, Self
from PIL import ImageFont, ImageDraw, Image
# from modules.data_updater.painter.style import *
# from modules.data_updater.painter.constants import *
# from modules.data_updater.painter.cell import *
from modules.data_updater.painter.base_container import BaseContainer
from modules.data_updater.painter.pixels import Pixels
from modules.data_updater.painter.container import Container
from modules.data_updater.painter.text import Text
from modules.data_updater.painter.united_cell import UnitedCell
from modules.data_updater.painter.cell import Cell


class Border(BaseContainer):
    _width: int
    _length: int
    _color: int
    _orientation: str

    def draw(self, canvas):
        if self._orientation == "horizontal":
            canvas.line((self.pixels.left_x, self.pixels.top_y, self.pixels.left_x + self._length,
                         self.pixels.top_y),
                        fill=self._color,
                        width=self._width)

        elif self._orientation == "vertical":
            canvas.line((self.pixels.left_x, self.pixels.top_y, self.pixels.left_x,
                         self.pixels.top_y + self._length),
                        fill=self._color,
                        width=self._width)


class Table(BaseContainer):
    _content: List
    _columns_width: List[int]
    _rows_height: List[int]
    _same_column_width: List[int]
    _same_row_height: List[int]
    _width: int = 0
    _height: int = 0
    pixels = Pixels
    _vertical_alignment: str = "center"
    _horizontal_alignment: str = "center"
    _outline_size: int | None = None
    _outline_color: str | None = None
    _vertical_borders: List[Border]
    _horizontal_borders: List[Border]

    def __init__(self, left_top=(0, 0), content=None):
        self.pixels = Pixels(container=self)
        self._width = len(content[0])
        self._height = len(content)
        self._set_content(content)
        self._same_column_width = [column for column in range(self._width)]
        self._same_row_height = [row for row in range(self._height)]

        self._vertical_borders = [Border() for _ in range(self._width + 1)]
        for i in self._vertical_borders:
            i._orientation = "vertical"

        self._horizontal_borders = [Border() for _ in range(self._height + 1)]
        for i in self._horizontal_borders:
            i._orientation = "horizontal"

        self.pixels.left_top = left_top

        self._update_pixels()

    def _cell_outline_changed(self, value: str, cell: Cell):
        print(value)

    def _changed(self, field):
        if field == "padding":
            self._update_pixels()

    @property
    def outline_size(self):
        return self._outline_size

    @outline_size.setter
    def outline_size(self, value):
        self._outline_size = value
        self._update_content()

    @property
    def outline_color(self):
        return self._outline_color

    @outline_color.setter
    def outline_color(self, value):
        self._outline_color = value
        self._update_content()

    def _update_content(self):
        for row in range(self._height):
            for column in range(self._width):
                cell = self._content[row][column]
                cell._table = self

                if self._cell_is_active(cell):
                    if self.pixels.padding:
                        cell.pixels.padding = self.pixels.padding

                    if self.outline_size:
                        cell.outline_size = self.outline_size

                    if self.outline_color:
                        cell.outline_color = self.outline_color

                    cell.vertical_alignment = self._vertical_alignment
                    cell.horizontal_alignment = self._horizontal_alignment
                    cell.coordinates = row, column
                else:
                    cell.pixels.padding = 0
                    cell.pixels.outline_size = 0
                    cell.pixels.width = 0
                    cell.pixels.height = 0

    def _set_content(self, content):
        self._content = [[Cell() for _ in range(self._width)] for _ in range(self._height)]
        for row in range(self._height):
            for column in range(self._width):
                self._content[row][column].content = content[row][column]

    def __getitem__(self, index):
        return self._content[index]

    def _update_pixels(self):
        self._update_content()
        self._update_columns_width()
        self._update_rows_height()
        self._update_cells_size()
        self._update_united_cells_size()
        self.pixels.width = sum(self._columns_width)
        self.pixels.height = sum(self._rows_height)

        current_pos = self.pixels.left_top
        for row in range(self._height):
            for column in range(self._width):
                cell = self._content[row][column]
                if self._cell_is_active(cell):
                    cell.pixels.left_top = current_pos

                current_pos = current_pos[0] + self._columns_width[column], current_pos[1]

            current_pos = self.pixels.left_x, current_pos[1] + self._rows_height[row]
        pass

    def _update_columns_width(self):
        self._columns_width = [0 for i in range(self._width)]

        for column in range(self._width):
            for row in range(self._height):
                cell = self._content[row][column]
                if not isinstance(cell, UnitedCell):
                    self._columns_width[column] = max(self._columns_width[column], cell.pixels.width)

        for column in range(self._width):
            for row in range(self._height):
                cell = self._content[row][column]
                if isinstance(cell, UnitedCell) and cell.parent is None:
                    width = cell.pixels.width
                    start = cell.coordinates[1]
                    end = start + cell.width
                    width -= sum(self._columns_width[start:end])
                    width = max(0, width)
                    width = (width + cell.width - 1) // cell.width
                    for i in range(start, end):
                        self._columns_width[i] += width

    def _update_rows_height(self):
        self._rows_height = [0 for i in range(self._height)]

        for row in range(self._height):
            for column in range(self._width):
                cell = self._content[row][column]
                if not isinstance(cell, UnitedCell):
                    self._rows_height[row] = max(self._rows_height[row], cell.pixels.height)

        for row in range(self._height):
            row_height = 0
            for column in range(self._width):
                cell = self._content[row][column]
                if isinstance(cell, UnitedCell) and cell.parent is None:
                    height = cell.pixels.height
                    start = cell.coordinates[0]
                    end = start + cell.height
                    height -= sum(self._rows_height[start:end])
                    height = max(0, height)
                    height = (height + cell.height - 1) // cell.height
                    for i in range(start, end):
                        self._rows_height[i] += height

    def _update_cells_size(self):
        for row in range(self._height):
            for column in range(self._width):
                cell = self._content[row][column]
                if isinstance(cell, UnitedCell):
                    continue

                self._content[row][column].pixels.width = self._columns_width[column]
                self._content[row][column].pixels.height = self._rows_height[row]

    def _update_united_cells_size(self):
        for row in range(self._height):
            for column in range(self._width):
                cell = self._content[row][column]
                if isinstance(cell, UnitedCell) and cell.parent is None:
                    width_start = cell.coordinates[1]
                    width_end = cell.width + width_start
                    height_start = cell.coordinates[0]
                    height_end = cell.height + height_start
                    width = sum(self._columns_width[width_start:width_end]) - cell.width + 1
                    height = sum(self._rows_height[height_start:height_end]) - cell.height + 1
                    self._content[row][column].pixels.width = width
                    self._content[row][column].pixels.height = height

    def squeeze(self):
        for row in range(self._height):
            for column in range(self._width):
                self._content[row][column].squeeze()

        self._update_pixels()

    def _cell_is_active(self, cell: Cell) -> bool:
        return isinstance(cell, UnitedCell) and cell.parent is None or not isinstance(cell, UnitedCell)

    def draw(self, canvas):
        for row in range(self._height):
            for column in range(self._width):
                cell = self._content[row][column]
                if self._cell_is_active(cell):
                    cell.draw_inside(canvas)

        for row in range(self._height):
            for column in range(self._width):
                cell = self._content[row][column]
                if self._cell_is_active(cell):
                    cell.draw_content(canvas)
                    cell.draw_outline(canvas)

    def _unite_blocks(self, cell1: UnitedCell, cell2: UnitedCell):
        # Unite blocks of united cells
        if cell1.parent is not None:
            cell1 = cell1.parent

        if cell2.parent is not None:
            cell2 = cell2.parent

        if cell1.coordinates > cell2.coordinates:
            cell1, cell2 = cell2, cell1

        # Exception check
        if not (cell1.top_row == cell2.top_row and  # rows same
                cell1.bottom_row == cell2.bottom_row and
                abs(cell1.right_column - cell2.left_column) <= 1 or
                cell1.left_column == cell2.left_column and  # columns same
                cell1.right_column == cell2.right_column and
                abs(cell1.bottom_row - cell2.top_row) <= 1):
            raise ValueError('Blocks are not neighbors')

        main_cell = UnitedCell()
        main_cell.set_main(cell1, cell2)
        self._content[main_cell.row][main_cell.column] = main_cell

        for row in range(cell1.top_row, cell2.bottom_row + 1):
            for column in range(cell1.left_column, cell2.right_column + 1):
                if (row, column) == main_cell.coordinates:  # skip main
                    continue

                cell = self[row][column]
                child_cell = UnitedCell()
                child_cell.set_parent(main_cell, cell)
                self._content[row][column] = child_cell

    def unite_cells(self, coordinates1, coordinates2):
        cell1 = self._content[coordinates1[0]][coordinates1[1]]
        cell2 = self._content[coordinates2[0]][coordinates2[1]]
        if isinstance(cell1, UnitedCell):
            if cell1.parent is None:
                united_cell1 = cell1.parent
            united_cell1 = cell1
        else:
            united_cell1 = UnitedCell.convert_cell_to_united_cell(cell1)
        if isinstance(cell2, UnitedCell):
            if cell2.parent is None:
                united_cell2 = cell2.parent
            else:
                united_cell2 = cell2
        else:
            united_cell2 = UnitedCell.convert_cell_to_united_cell(cell2)

        self._unite_blocks(united_cell1, united_cell2)


if __name__ == "__main__":
    pass
