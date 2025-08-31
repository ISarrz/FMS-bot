from __future__ import annotations
from modules.data_updater.painter.container import Container


class Cell(Container):
    _coordinates: tuple[int, int] = (0, 0)
    _table = None

    @property
    def outline_color(self):
        return self._outline_color

    @outline_color.setter
    def outline_color(self, value):
        self._outline_color = value
        self.left_outline_color = value
        self.right_outline_color = value
        self.top_outline_color = value
        self.bottom_outline_color = value

    @property
    def left_outline_color(self):
        return self._left_outline_color

    @left_outline_color.setter
    def left_outline_color(self, value):
        self._left_outline_color = value
        if self._table is not None:
            self._table._cell_outline_changed("left", self)

    @property
    def right_outline_color(self):
        return self._right_outline_color

    @right_outline_color.setter
    def right_outline_color(self, value):
        self._right_outline_color = value
        if self._table is not None:
            self._table._cell_outline_changed("right", self)

    @property
    def top_outline_color(self):
        return self._top_outline_color

    @top_outline_color.setter
    def top_outline_color(self, value):
        self._top_outline_color = value
        if self._table is not None:
            self._table._cell_outline_changed("top", self)

    @property
    def bottom_outline_color(self):
        return self._bottom_outline_color

    @bottom_outline_color.setter
    def bottom_outline_color(self, value):
        self._bottom_outline_color = value
        if self._table is not None:
            self._table._cell_outline_changed("bottom", self)

    @property
    def outline_size(self):
        return self._outline_size

    @outline_size.setter
    def outline_size(self, value):
        self._outline_size = value
        if self._table is not None:
            self._table._cell_outline_changed("size", self)

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
