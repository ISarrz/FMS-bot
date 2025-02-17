from PIL import ImageDraw
from .cell import Cell


class UnitedCell(Cell):
    """
    United cells are grouped in rect of cells.
    Left top cell considered main and contains value.
    Not main cells don`t have value and linked with main cell.
    """

    def __init__(self, row=None, column=None, left_top=None, right_bottom=None, value='', parent=None, style=None,
                 ):
        row = row if parent else left_top[0]
        column = column if parent else left_top[1]
        super().__init__(row, column, value, style)
        self.width = right_bottom[1] - left_top[1] + 1
        self.height = right_bottom[0] - left_top[0] + 1

        # Coordinates of united block
        self.left_top = left_top
        self.right_bottom = right_bottom

        # United cells with parents are always empty
        self.parent = parent
        self.value = value if not self.parent else None

    @property
    def value(self):
        return self.value if not self.parent else self.parent.value

    @value.setter
    def value(self, value):
        if self.parent:
            self.parent.value = value
        else:
            self.value = value

    def get_left_top(self):
        if self.parent:
            return self.parent.left_top
        else:
            return self.left_top

    def get_right_bottom(self):
        if self.parent:
            return self.parent.right_bottom
        else:
            return self.right_bottom
