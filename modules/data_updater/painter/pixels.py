import dataclasses


@dataclasses.dataclass
class Pixels:
    _left_top: tuple[int, int] = (0, 0)
    _right_bottom: tuple[int, int] = (0, 0)
    _padding: int = 0
    _margin: int = 0

    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, value):
        self._padding = value

    @property
    def margin(self):
        return self._margin

    @margin.setter
    def margin(self, value):
        self._margin = value

    @property
    def left_top(self):
        return self._left_top

    @property
    def right_bottom(self):
        return self._right_bottom

    @property
    def left_x(self):
        return self.left_top[0]

    @property
    def top_y(self):
        return self.left_top[1]

    @property
    def right_x(self):
        return self.right_bottom[0]

    @property
    def bottom_y(self):
        return self.right_bottom[1]

    @property
    def width(self):
        return self.right_x - self.left_x

    @property
    def height(self):
        return self.bottom_y - self.top_y

    @property
    def center(self):
        return (self.left_x + self.right_x) // 2, (self.top_y + self.bottom_y) // 2

    @left_top.setter
    def left_top(self, value: tuple[int, int]):
        width = self.width
        height = self.height
        self._left_top = value
        self._right_bottom = self.left_x + width, self.top_y + height


    @right_bottom.setter
    def right_bottom(self, value: tuple[int, int]):
        width = self.width
        height = self.height
        self._right_bottom = value
        self._left_top = self.right_x - width, self.bottom_y - height

    @width.setter
    def width(self, value):
        self._right_bottom = self.left_top[0] + value, self.right_bottom[1]

    @height.setter
    def height(self, value):
        self._right_bottom = self.right_bottom[0], self.left_top[1] + value

    @center.setter
    def center(self, value):
        width = self.width
        height = self.height
        left_width = (width + 1) // 2
        right_width = width // 2
        top_height = (height + 1) // 2
        bottom_height = (height + 1) // 2

        self.left_top = value[0] - left_width, value[1] - top_height
        self.right_bottom = value[0] + right_width, value[1] + bottom_height
