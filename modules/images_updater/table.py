from .style import CellStyle
from .cell import *

im = Image.new('RGB', (500, 500), '#FFFFFF')
draw = ImageDraw.Draw(im)


class Table:
    """Allows you to create graphical tables with Pillow"""

    def __init__(self, matrix: list[list[str]], cell_style=CellStyle(ImageFont.load_default(20))):

        self.columns_width = []
        self.rows_height = []
        self.same_columns = []
        self.cell_style = cell_style

        self.width = len(matrix[0])
        self.height = len(matrix)
        self.matrix = [[Cell((row, col), matrix[row][col], cell_style=self.cell_style)
                        for col in range(self.width)] for row in range(self.height)]

        # Группы колонок и рядов одного размера (to do)
        # self.column_groups = None
        # self.row_groups = None

        self.same_columns = [False for _ in range(self.width)]
        # formatting table
        self._calculate_table_size()

    def _calculate_table_size(self):
        columns_width = [0 for _ in range(self.width)]
        rows_height = [0 for _ in range(self.height)]

        # usual cell size setting
        for row in range(self.height):
            for col in range(self.width):
                cell = self.get_cell((row, col))
                if not cell.unite:
                    columns_width[col] = max(columns_width[col], cell.pixel_width)
                    rows_height[row] = max(rows_height[row], cell.pixel_height)

        # united cell size setting
        for row in range(self.height):
            for column in range(self.width):
                cell = self.get_cell((row, column))
                if cell.unite and cell.parent is None:
                    width = cell.pixel_width
                    height = cell.pixel_height
                    width -= sum(columns_width[cell.left_top[1]:cell.right_bottom[1] + 1])
                    height -= sum(rows_height[cell.left_top[0]:cell.right_bottom[0] + 1])
                    width = max(0, width)
                    height = max(0, height)
                    width //= cell.width
                    height //= cell.height
                    for i in range(cell.left_top[1], cell.right_bottom[1] + 1):
                        columns_width[i] += width
                    for i in range(cell.left_top[0], cell.right_bottom[0] + 1):
                        rows_height[i] += height

        # find max same group value
        same_width = max([columns_width[column] if self.same_columns[column] else 0 for column in range(self.width)])

        # setting size for usual cells
        for row in range(self.height):
            for column in range(self.width):
                width, height = columns_width[column], rows_height[row]
                cell = self.get_cell((row, column))
                if not cell.unite:
                    if self.same_columns[column]:
                        cell.set_cell_size(same_width, height)
                        columns_width[column] = same_width
                    else:
                        cell.set_cell_size(width, height)

        # setting size for united cells
        for row in range(self.height):
            for col in range(self.width):
                cell = self.get_cell((row, col))
                if cell.unite and cell.parent is None:
                    width = sum(columns_width[cell.left_top[1]:cell.right_bottom[1] + 1])
                    height = sum(rows_height[cell.left_top[0]:cell.right_bottom[0] + 1])
                    cell.set_cell_size(width, height)

        # Баг в пересчете координат, надо подумать

        self.columns_width = columns_width
        self.rows_height = rows_height
        self._calculate_coordinates()

    def _calculate_coordinates(self):
        for row in range(self.height):
            for col in range(self.width):
                if self.get_cell((row, col)).parent is not None:
                    continue
                x = self.get_cell((row, col - 1)).get_xy2()[0] if col != 0 else 0
                y = self.get_cell((row - 1, col)).get_xy2()[1] if row != 0 else 0
                self.get_cell((row, col)).set_xy1((x, y))

    def autoformat(self):
        """Sets minimal size of all cells and formatting table."""
        for row in range(self.height):
            for column in range(self.width):
                self.get_cell((row, column)).set_minimal_size()
        self._calculate_table_size()
        self._calculate_coordinates()

    def set_same_columns(self, group: list[int]):
        for i in group:
            self.same_columns[i] = True

    def set_cell_style(self, coordinates: (int, int), style: CellStyle):
        self.get_cell(coordinates).set_cell_style(style)

    def set_cell_lines_style(self, coord: (int, int), styles: list[TextStyle]):
        cell = self.get_cell(coord)
        for i in range(len(styles)):
            style = styles[i]
            cell.lines[i][1] = style

    def set_area_lines_style(self, coord1: (int, int), coord2: (int, int), styles: list[TextStyle]):
        for i in range(coord1[0], coord2[0] + 1):
            for j in range(coord1[1], coord2[1] + 1):
                cell = self.get_cell((i, j))
                for g in range(min(len(styles), len(cell.lines))):
                    style = styles[g]
                    cell.lines[g][1] = style

    def set_area_style(self, coords1: (int, int), coords2: (int, int), style: CellStyle):
        for row in range(coords1[0], coords2[0] + 1):
            for col in range(coords1[1], coords2[1] + 1):
                self.get_cell((row, col)).set_cell_style(style)

    def get_cell(self, coordinates: (int, int)) -> Cell:
        self._check_coordinates(coordinates)
        return self.matrix[coordinates[0]][coordinates[1]]

    def check_coordinates(self, coordinates: (int, int)) -> bool:
        row, column = coordinates
        if row < 0 or row >= self.height or column < 0 or column >= self.width:
            return False
        return True

    def _check_coordinates(self, coordinates: (int, int)):
        if not self.check_coordinates(coordinates):
            raise IndexError("Invalid coordinates")

    def check_rectangle(self, left_top, right_bottom) -> bool:
        if not self.check_coordinates(left_top) or not self.check_coordinates(right_bottom):
            return False
        if right_bottom[0] < left_top[0] or left_top[1] > right_bottom[1]:
            return False
        return True

    def _check_rectangle(self, left_top, right_bottom):
        if not self.check_rectangle(left_top, right_bottom):
            raise IndexError("Invalid coordinates")

    def draw(self, screen=None, margin=0):
        self._calculate_table_size()
        table_width = sum(self.columns_width) + self.cell_style.line_width
        table_height = sum(self.rows_height) + self.cell_style.line_width
        canvas_width = table_width + margin * 2
        canvas_height = table_height + margin * 2

        image1 = Image.new('RGB', (canvas_width, canvas_height), '#1e2124')

        image2 = Image.new('RGB', (table_width, table_height), '#1e2124')
        table = ImageDraw.Draw(image2)

        for row in range(self.height):
            for column in range(self.width):
                cell = self.get_cell((row, column))
                if cell.parent is None:
                    cell.draw(table)

        image1.paste(image2, (margin, margin))
        return image1

    @staticmethod
    def _unite_cells(cell1: Cell, cell2: Cell):
        # Unite single cells

        if cell1.coords == cell2.coords:
            return

        # calculating Coordinates of united box
        left_top = (min(cell1.coords[0], cell2.coords[0]), min(cell1.coords[1], cell2.coords[1]))
        right_bottom = (max(cell1.coords[0], cell2.coords[0]), max(cell1.coords[1], cell2.coords[1]))

        # cell1 is main
        if left_top != cell1.coords:
            cell1, cell2 = cell2, cell1

        pixel_width = cell2.xy2[0] - cell1.xy1[0]
        pixel_height = cell2.xy2[1] - cell1.xy1[1]
        width = right_bottom[1] - left_top[1] + 1
        height = right_bottom[0] - left_top[0] + 1

        # Checking the neighbourhood of cells
        row_delta = abs(cell1.coords[0] - cell2.coords[0])
        column_delta = abs(cell1.coords[1] - cell2.coords[1])

        if row_delta > 1 or column_delta > 1 or row_delta == 1 and column_delta == 1:
            raise ValueError('Cells are not neighbors')

        cell1.set_main(right_bottom, (width, height), (pixel_width, pixel_height))
        cell2.set_parent(cell1)

    def _unite_blocks(self, cell1: Cell, cell2: Cell):
        # Unite blocks of united cells
        if cell1.parent is not None:
            cell1 = self.get_cell(cell1.parent.coords)
        if cell2.parent is not None:
            cell2 = self.get_cell(cell2.parent.coords)

        if cell1.coords == cell2.coords:
            return

        # calculating borders
        left_top = min(cell1.coords, cell2.coords)
        right_bottom = max(cell1.right_bottom, cell2.right_bottom)

        # Cell1 is main
        if cell1.coords != left_top:
            cell1, cell2 = cell2, cell1

        # Exception check
        if not (cell1.left_top[0] == cell2.left_top[0] and  # rows same
                cell1.right_bottom[0] == cell2.right_bottom[0] and
                abs(cell1.right_bottom[1] - cell2.left_top[1]) <= 1 or
                cell1.left_top[1] == cell2.left_top[1] and  # columns same
                cell1.right_bottom[1] == cell2.right_bottom[1] and
                abs(cell1.right_bottom[0] - cell2.left_top[0]) <= 1):
            raise ValueError('Block are not neighbors')

        # Setting values
        width = right_bottom[1] - left_top[1] + 1
        height = right_bottom[0] - left_top[0] + 1
        pixel_width = cell2.xy2[0] - cell1.xy1[0]
        pixel_height = cell1.xy2[1] - cell2.xy1[1]
        cell1.set_main(right_bottom, (width, height), (pixel_width, pixel_height))

        for row in range(left_top[0], right_bottom[0] + 1):
            for col in range(left_top[1], right_bottom[1] + 1):
                if (row, col) == left_top:  # skip main
                    continue
                self.get_cell((row, col)).set_parent(cell1)

    def _unite_cell_with_block(self, cell1: Cell, cell2: Cell):
        # Unite single cell with block united cells

        if cell1.coords == cell2.coords:
            return

        # calculating borders
        left_top = min(cell1.coords, cell2.parent.coords)
        right_bottom = max(cell1.coords, cell2.parent.coords)
        width = right_bottom[1] - left_top[1] + 1
        height = right_bottom[0] - left_top[0] + 1

        # Checking the neighbourhood of cells
        if abs(cell2.left_top[0] == cell2.right_bottom[0]):
            if cell1.coords[0] != cell2.left_top[0]:
                raise ValueError('Cells are not neighbors')

        elif abs(cell2.left_top[1] == cell2.right_bottom[1]):
            if cell1.coords[1] != cell2.left_top[1]:
                raise ValueError('Cells are not neighbors')

        else:
            raise ValueError('Cells are not neighbors')

        pixel_width = cell2.xy2[0] - cell1.xy1[0]
        pixel_height = cell2.xy2[1] - cell1.xy1[1]
        main_cell = self.get_cell(left_top)
        main_cell.set_main(right_bottom, (width, height), (pixel_width, pixel_height))

        for row in range(left_top[0], right_bottom[0] + 1):
            for column in range(left_top[1], right_bottom[1] + 1):
                if (row, column) == left_top:
                    continue
                self.get_cell((row, column)).set_parent(main_cell)

    def unite_area(self, left_top, right_bottom, value=None):
        if not self.check_coordinates(left_top) or not self.check_coordinates(right_bottom):
            raise IndexError('Invalid coordinates')

        value = value if value else self.get_cell(left_top).text

        width = right_bottom[1] - left_top[1] + 1
        height = right_bottom[0] - left_top[0] + 1
        main_cell = self.get_cell(left_top)
        child_cell = self.get_cell(right_bottom)
        pixel_width = child_cell.xy2[0] - main_cell.xy1[0]
        pixel_height = child_cell.xy2[1] - main_cell.xy1[1]

        self.get_cell(left_top).set_main(right_bottom, (width, height), (pixel_width, pixel_height))

        for row in range(left_top[0], right_bottom[0] + 1):
            for column in range(left_top[1], right_bottom[1] + 1):
                if (row, column) == left_top:
                    continue
                self.get_cell((row, column)).set_parent(main_cell)

    def unite_cells(self, coordinates1, coordinates2):
        self._check_coordinates(coordinates1)
        self._check_coordinates(coordinates2)

        cell1 = self.get_cell(coordinates1)
        cell2 = self.get_cell(coordinates2)

        if not cell1.unite and not cell2.unite:
            self._unite_cells(cell1, cell2)
        elif not cell1.unite and cell2.unite:
            self._unite_cell_with_block(cell1, cell2)
        elif cell1.unite and not cell2.unite:
            self._unite_cell_with_block(cell2, cell1)
        elif cell1.unite and cell2.unite:
            self._unite_blocks(cell1, cell2)
