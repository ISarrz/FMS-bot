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


class Cell(Container):
    _coordinates: tuple[int, int] = (0, 0)

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value):
        self._coordinates = value

    @property
    def row(self):
        return self.coordinates[0]

    @row.setter
    def row(self, value):
        self.coordinates = (value, self.column)

    @property
    def column(self):
        return self.coordinates[1]

    @column.setter
    def column(self, value):
        self.coordinates = (self.row, value)


class UnitedCell(Cell):
    parent: None | Self = None
    width: int
    height: int
    left_top: tuple[int, int]
    right_bottom: tuple[int, int]

    # def __init__(self, cell: Cell) -> None:
    #     super().__init__(fill=cell._fill, radius=cell._radius)
    #     self.pixels = cell.pixels
    #     self._update_pixels()

    @property
    def left_column(self):
        return self.left_top[0]

    @staticmethod
    def convert_cell_to_united_cell(cell: Cell) -> UnitedCell:
        united_cell = UnitedCell()
        united_cell.pixels = cell.pixels
        united_cell.content = cell.content
        united_cell.coordinates = cell.coordinates
        united_cell.left_top = cell.coordinates
        united_cell.right_bottom = cell.coordinates
        united_cell.outline_size = cell.outline_size
        united_cell.outline_color = cell.outline_color
        united_cell.fill = cell.fill
        united_cell._radius = cell._radius
        united_cell.vertical_alignment = cell.vertical_alignment
        united_cell.horizontal_alignment = cell.horizontal_alignment
        united_cell.left_outline_color = cell.left_outline_color
        united_cell.right_outline_color = cell.right_outline_color
        united_cell.top_outline_color = cell.top_outline_color
        united_cell.bottom_outline_color = cell.bottom_outline_color

        return united_cell

    @property
    def right_column(self):
        return self.right_bottom[0]

    @property
    def top_row(self):
        return self.left_top[1]

    @property
    def bottom_row(self):
        return self.right_bottom[1]

    def set_parent(self, parent: Self, child_cell):
        self.pixels.width = 0
        self.pixels.height = 0
        self.parent = parent
        self.width = 1
        self.height = 1
        self.coordinates = child_cell.coordinates
        self.left_top = self.coordinates

    def set_main(self, main_cell: Cell, child_cell: Cell):
        self.pixels.left_top = main_cell.pixels.left_top
        self.pixels.width = child_cell.pixels.right_x - main_cell.pixels.left_x + 1
        self.pixels.height = child_cell.pixels.bottom_y - main_cell.pixels.top_y + 1

        if not isinstance(main_cell, UnitedCell):
            main_cell = UnitedCell.convert_cell_to_united_cell(main_cell)

        if not isinstance(child_cell, UnitedCell):
            child_cell = UnitedCell.convert_cell_to_united_cell(child_cell)

        self.width = child_cell.right_column - main_cell.left_column + 1
        self.height = child_cell.bottom_row - main_cell.top_row + 1

        self.coordinates = main_cell.coordinates
        self.left_top = main_cell.coordinates
        self.right_bottom = (self.top_row + self.height - 1, self.left_column + self.width - 1)
        self.horizontal_alignment = main_cell.horizontal_alignment
        self.vertical_alignment = main_cell.vertical_alignment
        self._outline_size = main_cell.outline_size
        self.content = main_cell.content
        self.pixels.padding = main_cell.pixels.padding


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

    def __init__(self, left_top=(0, 0), content=None):
        self.pixels = Pixels(container=self)
        self._set_content(content)
        self._same_column_width = [column for column in range(self._width)]
        self._same_row_height = [row for row in range(self._height)]
        self.pixels.left_top = left_top

        self._update_pixels()

    def _changed(self, field):
        pass
        if field == "padding":
            self._update_content()

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

                if not isinstance(cell, UnitedCell) or isinstance(cell, UnitedCell) and cell.parent is None:
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
        self._width = len(content[0])
        self._height = len(content)
        self._content = [[Cell() for _ in range(self._width)] for _ in range(self._height)]
        for row in range(self._height):
            for column in range(self._width):
                self._content[row][column].content = content[row][column]

    def __getitem__(self, index):
        return self._content[index]

    def _update_pixels(self):
        self._update_columns_width()
        self._update_rows_height()
        self._update_cells_size()
        self._update_united_cells_size()
        self.pixels.width = sum(self._columns_width)
        self.pixels.height = sum(self._rows_height)
        self._update_content()

        current_pos = self.pixels.left_top
        for row in range(self._height):
            for column in range(self._width):
                cell = self._content[row][column]
                if isinstance(cell, UnitedCell):
                    if cell.parent is None:
                        cell.pixels.left_top = current_pos
                    else:
                        pass
                else:
                    cell.pixels.left_top = current_pos

                current_pos = current_pos[0] + self._columns_width[column] - 1, current_pos[1]

            current_pos = self.pixels.left_x, current_pos[1] + self._rows_height[row] - 1
        pass

    def _update_columns_width(self):
        self._columns_width = [0 for i in range(self._width)]
        same_column_width_groups = dict()
        for group_ind in self._same_column_width:
            same_column_width_groups[group_ind] = []

        for group_ind, column_ind in enumerate(self._same_column_width):
            same_column_width_groups[group_ind].append(column_ind)

        for column in range(self._width):
            column_width = 0
            for row in range(self._height):
                cell = self._content[row][column]
                if isinstance(cell, UnitedCell):
                    continue
                else:
                    self._columns_width[column] = max(self._columns_width[column], cell.pixels.width)

        for group in same_column_width_groups.values():
            width = max(self._columns_width[column_ind] for column_ind in group)
            for column_ind in group:
                self._columns_width[column_ind] = width

        for column in range(self._width):
            column_width = 0
            for row in range(self._height):
                cell = self._content[row][column]
                if isinstance(cell, UnitedCell) and cell.parent is None:
                    width = cell.pixels.width
                    start = cell.coordinates[0]
                    end = start + cell.width
                    width -= sum(self._columns_width[start:end])
                    width = (width + cell.width - 1) // cell.width
                    for i in range(start, end):
                        self._columns_width[i] += width

    def _update_rows_height(self):
        self._rows_height = [0 for i in range(self._height)]
        same_row_height_groups = dict()
        for group_ind in self._same_row_height:
            same_row_height_groups[group_ind] = []

        for group_ind, row_ind in enumerate(self._same_row_height):
            same_row_height_groups[group_ind].append(row_ind)

        for row in range(self._height):
            row_height = 0
            for column in range(self._width):
                cell = self._content[row][column]
                if isinstance(cell, UnitedCell):
                    continue
                self._rows_height[row] = max(self._rows_height[row], cell.pixels.height)

        for group in same_row_height_groups.values():
            height = max(self._rows_height[row_ind] for row_ind in group)
            for row_ind in group:
                self._rows_height[row_ind] = height

        for row in range(self._height):
            row_height = 0
            for column in range(self._width):
                cell = self._content[row][column]
                if isinstance(cell, UnitedCell) and cell.parent is None:
                    height = cell.pixels.height
                    start = cell.coordinates[1]
                    end = start + cell.height
                    height -= sum(self._rows_height[start:end])
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
                    width_start = cell.coordinates[0]
                    width_end = cell.width + width_start
                    height_start = cell.coordinates[1]
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

    def draw(self, canvas):
        for row in range(self._height):
            for column in range(self._width):
                cell = self._content[row][column]
                if isinstance(cell, UnitedCell):
                    if not cell.parent:
                        cell.draw(canvas)
                else:
                    cell.draw(canvas)

    def _unite_cells(self, cell1: Cell, cell2: Cell):
        # cell1 is main(left top)
        if cell1.coordinates > cell2.coordinates:
            cell1, cell2 = cell2, cell1

        width = cell2.column - cell1.column + 1
        height = cell2.row - cell1.row + 1

        if width + height > 3:
            raise ValueError('Cells are not neighbors')

        main_cell = UnitedCell()
        main_cell.set_main(cell1, cell2)

        child_cell = UnitedCell()
        child_cell.set_parent(main_cell, cell2)

        self._content[main_cell.row][main_cell.column] = main_cell
        self._content[child_cell.row][child_cell.column] = child_cell

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
                child_cell.set_parent(main_cell, cell2)
                self._content[row][column] = child_cell

    def _unite_cell_with_block(self, cell1: Cell, cell2: Cell):
        # Unite single cell with block united cells
        if cell1.coordinates > cell2.coordinates:
            cell1, cell2 = cell2, cell1

        if not isinstance(cell1, UnitedCell):
            cell1 = UnitedCell.convert_cell_to_united_cell(cell1)

        if not isinstance(cell2, UnitedCell):
            cell2 = UnitedCell.convert_cell_to_united_cell(cell2)

        self._unite_blocks(cell1, cell2)

    def unite_cells(self, coordinates1, coordinates2):

        cell1 = self._content[coordinates1[0]][coordinates1[1]]
        cell2 = self._content[coordinates2[0]][coordinates2[1]]

        if not isinstance(cell1, UnitedCell) and not isinstance(cell2, UnitedCell):
            self._unite_cells(cell1, cell2)

        elif not cell1.unite and cell2.unite:
            self._unite_cell_with_block(cell1, cell2)

        elif cell1.unite and not cell2.unite:
            self._unite_cell_with_block(cell2, cell1)
        elif cell1.unite and cell2.unite:
            self._unite_blocks(cell1, cell2)


if __name__ == "__main__":
    pass
