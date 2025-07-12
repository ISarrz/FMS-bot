from PIL import Image, ImageDraw, ImageFont
from modules.data_updater.painter.style import *


class Cell:
    def __init__(self, cords: (int, int), text="", cell_style=CellStyle(TextStyle(ImageFont.load_default(20)))):
        self.coords = cords
        self.width = 1
        self.height = 1
        self.text_width = 1
        self.text_height = 1
        self.xy1 = (0, 0)
        self.xy2 = (0, 0)
        # self.center = (0, 0)
        self.pixel_width = 20
        self.pixel_height = 20
        self.style = cell_style
        self.lines = []
        self.text = text

        self.parent = None
        self.unite = False
        self.right_bottom = self.coords
        self.left_top = self.coords

        self.set_text(text)
        self.set_minimal_size()

    def set_minimal_size(self, width=True, height=True):
        if width:
            self.pixel_width = self.text_width + self.style.padding * 2 + self.style.line_width
        if height:
            self.pixel_height = self.text_height + self.style.padding * 2 + self.style.line_width
        self.pixel_height = max(self.pixel_height, self.style.minimum_height)
        self.pixel_width = max(self.pixel_width, self.style.minimum_width)
        self.xy2 = (self.xy1[0] + self.pixel_width, self.xy1[1] + self.pixel_height)

    def _calc_text_size(self):
        image = Image.new('RGB', (500, 500))
        screen = ImageDraw.Draw(image)
        self.text_width, self.text_height = 0, 0
        for i in range(len(self.lines)):
            string, font = self.lines[i]
            _, _, width, line_spacing = screen.textbbox((0, 0), string, font=font.font)

            self.text_width = max(self.text_width, width)
            self.text_height += line_spacing
            if i != 0:
                # self.text_height += line_spacing
                self.text_height += font.spacing

        # self.text_width += self.style.line_width * 2 + self.style.padding * 2
        # self.text_height += self.style.line_width * 2 + self.style.padding * 2

    def set_cell_style(self, style: CellStyle):
        self.style = style
        self.set_text(self.text)
        self._calc_text_size()

    def set_xy1(self, xy1: (int, int)):
        self.xy1 = xy1
        self.set_minimal_size(False, False)

    def set_text(self, text):
        self.text = text
        self.lines = text.split('\n') if text else ['']
        self.lines = [[i, self.style.text_style] for i in self.lines]
        self._calc_text_size()
        return self

    def set_parent(self, parent):
        self.parent = parent
        self.set_cell_style(parent.style)
        self.set_xy1((0, 0))
        self.set_text('')
        self.set_minimal_size()
        self.unite = True
        self.xy1 = parent.xy1
        self.xy2 = parent.xy2

    def set_line_style(self, line: int, style: TextStyle):
        self.style = style
        self.lines[line][1] = style
        return self

    def set_cell_size(self, width: int = None, height: int = None):
        if width is not None:
            self.pixel_width = width
        if height is not None:
            self.pixel_height = height
        self.set_minimal_size(False, False)

    def set_main(self, right_bottom: (int, int), size: (int, int), pixel_size: (int, int)):
        self.right_bottom = right_bottom
        self.set_cell_size(pixel_size[0], pixel_size[1])
        self.width = size[0]
        self.height = size[1]
        self.set_minimal_size(False, False)
        self.unite = True

    def get_xy1(self):
        return self.parent.xy1 if self.parent is not None else self.xy1

    def get_xy2(self):
        return self.parent.xy2 if self.parent is not None else self.xy2

    def get_width(self):
        return self.parent.width if self.parent is not None else self.width

    def get_height(self):
        return self.parent.height if self.parent is not None else self.height

    def get_right_bottom(self):
        return self.parent.right_bottom if self.parent is not None else self.right_bottom

    def get_left_top(self):
        return self.parent.left_top if self.parent is not None else self.left_top

    def draw(self, screen: ImageDraw):
        """Receive image and draw cell on it"""

        xy1 = self.xy1
        xy2 = self.xy2

        screen.rectangle((xy1, xy2), fill=self.style.fill, width=0, outline=None)

        hw = (self.style.line_width - 1) // 2
        w = self.style.line_width

        color = self.style.outline_color

        # Логика покинула меня, я хз откуда тут -1, но оно работает
        # top
        screen.line([xy1[0], xy1[1] + hw, xy2[0] + w - 1, xy1[1] + hw], fill=color, width=w)
        # right
        screen.line([xy2[0] + hw, xy1[1] + hw, xy2[0] + hw, xy2[1] + hw], fill=color, width=w)
        # bottom
        screen.line([xy1[0], xy2[1] + hw, xy2[0] + w - 1, xy2[1] + hw], fill=color, width=w)
        # left
        screen.line([xy1[0] + hw, xy1[1] + hw, xy1[0] + hw, xy2[1] + hw], fill=color, width=w)

        # Рисовка текста

        center = ((xy1[0] + xy2[0] + self.style.line_width) // 2, (xy1[1] + xy2[1] + self.style.line_width) // 2)
        cur_x, cur_y = xy1[0], center[1]
        cur_y -= self.text_height // 2

        for i in range(len(self.lines)):
            string, font = self.lines[i]
            _, _, width, line_spacing = screen.textbbox((0, 0), string, font=font.font)

            alignment = self.style.text_style.alignment

            if alignment == 'center':
                cur_x = center[0] - width // 2
            elif alignment == 'left':
                cur_x = xy1[0]
            elif alignment == 'right':
                cur_x = xy2[0] - width

            screen.text((cur_x, cur_y), string, fill=font.color, font=font.font)
            cur_y += line_spacing
            cur_y += font.spacing
