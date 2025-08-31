from typing import List
from PIL import ImageFont, ImageDraw, Image
from modules.data_updater.painter.table import Table
from modules.data_updater.painter.column import Column
from modules.data_updater.painter.text import Text


def table():
    # image = Image.new('RGB', (560, 1023), "#282b30")
    image = Image.new('RGB', (560, 1023), "white")
    canvas = ImageDraw.Draw(image)

    width, height = 2, 3
    content = [[None for _ in range(width)] for _ in range(height)]

    content[0][0] = Text(value="23.05", font="Roboto Medium Regular", size=40, fill="white")
    content[0][1] = Text(value="Z группа Б", font="Roboto Medium Regular", size=40, fill="white")

    column1 = Column(outline_size=0)
    column1._cell_space = -5
    column1.add(Text(value="8:30", font="Roboto Medium Regular", size=25, fill="#424549"))
    column1.add(Text(value="1", font="Roboto Medium Regular", size=40, fill="white"))
    column1.add(Text(value="9:15", font="Roboto Medium Regular", size=25, fill="#424549"))

    content[1][0] = column1
    content[1][1] = Text(value="Математика", font="Roboto Medium Regular", size=30, fill="white")

    column2 = Column(outline_size=0)
    column2.add(Text(value="9:25", font="Roboto Medium Regular", size=25, fill="#424549"))
    column2.add(Text(value="2", font="Roboto Medium Regular", size=40, fill="white"))
    column2.add(Text(value="10:10", font="Roboto Medium Regular", size=25, fill="#424549"))
    content[2][0] = column2
    content[2][1] = Text(value="Математика", font="Roboto Medium Regular", size=30, fill="white")

    table = Table(content=content, left_top=(10, 10))
    table.pixels.padding = 0
    table.unite_cells((1, 1), (2, 1))
    table[0][0].fill = "#282b30"
    table[0][1].fill = "#282b30"
    table[1][0].fill = "#282b30"
    table[1][0].pixels.padding = 0
    table[1][1].fill = "#424549"
    table[1][1].outline_color = "#36393e"
    table[1][1].pixels.padding = 0
    table[1][1].outline_size = 0
    table[2][0].fill = "#282b30"
    table[2][0].pixels.padding = 0
    table[2][1].fill = "#424549"
    table[2][1].outline_color = "#36393e"
    table[2][1].outline_size = 0
    # table.unite_cells((0, 1), (1, 1))
    # table.unite_cells((0, 0), (1, 1))
    # table.squeeze()
    # table._update_pixels()
    table.draw(canvas)

    image.save("text_image.png")
    image.show()


def rect():
    image = Image.new('RGB', (500, 500), "yellow")
    canvas = ImageDraw.Draw(image)

    canvas.rounded_rectangle((10, 10, 40, 40),
                             radius=0,
                             fill=None,
                             outline="black",
                             width=1)
    image.save("text_image.png")
    image.show()


def text_rn():
    value = "Я люблю Милану Хаметову\nИ милашку Рубана"
    text = Text(value=value, font="Roboto Medium Regular", size=40, fill="black")
    text._horizontal_alignment = "center"
    text._line_space = -5

    image = Image.new('RGB', (800, 500), "white")
    canvas = ImageDraw.Draw(image)

    text.draw(canvas)

    image.save("text_image.png")
    image.show()


if __name__ == "__main__":
    table()
