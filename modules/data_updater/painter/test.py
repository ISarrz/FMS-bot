from typing import List
from PIL import ImageFont, ImageDraw, Image
from modules.data_updater.painter.table import Table
from modules.data_updater.painter.column import Column
from modules.data_updater.painter.text import Text
from modules.time import *

def table():
    # image = Image.new('RGB', (560, 1023), "#282b30")
    image = Image.new('RGB', (560, 1023), "white")
    canvas = ImageDraw.Draw(image)

    width, height = 2, 3
    content = [[None for _ in range(width)] for _ in range(height)]

    content[0][0] = Text(value="23.05", font="Roboto Black", size=40, fill="white")
    content[0][1] = Text(value="Z группа Б", font="Roboto Black", size=40, fill="white")

    column1 = Column(outline_width=0)
    column1._cell_space = -5
    column1.add(Text(value="8:30", font="Roboto Black", size=20, fill="#424549"))
    column1.add(Text(value="1", font="Roboto Black", size=40, fill="white"))
    column1.add(Text(value="9:15", font="Roboto Black", size=20, fill="#424549"))

    content[1][0] = column1
    content[1][1] = Text(value="Математика\naas", font="Roboto Bold", size=30, fill="white")

    column2 = Column(outline_width=0)
    column2.add(Text(value="9:25", font="Roboto Black", size=20, fill="#424549"))
    column2.add(Text(value="2", font="Roboto Black", size=40, fill="white"))
    column2.add(Text(value="10:10", font="Roboto Black", size=20, fill="#424549"))
    content[2][0] = column2
    content[2][1] = Text(value="Математика", font="Roboto Bold", size=30, fill="white")

    table = Table(content=content, left_top=(10, 10))
    for i in range(table._height):
        for j in range(table._width):
            table[i][j].outline_width = 0
    # table.pixels.padding = 0
    table.unite_cells((1, 1), (2, 1))
    table[0][0].pixels.padding = 10
    table[0][1].pixels.padding = 10
    # расписание
    for i in range(1, table._height):
        table[i][1].fill = "#424549"
        table[i][1].outline_color = "#36393e"
        table[i][1].pixels.padding = 20
        table[i][1].pixels.width = 400
        table[i][1].outline_width = 8
        table[i][1].horizontal_alignment = "center"


    # номера
    for i in range(0, table._height):
        table[i][0].fill =  "#282b30"
        table[i][0].outline_color = "#36393e"
        table[i][0].pixels.padding = 0
        table[i][0].outline_width = 0

    table[0][0].fill = "#282b30"
    table[0][1].fill = "#282b30"
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


def simple():
    image = Image.new('RGB', (560, 1023), "white")
    canvas = ImageDraw.Draw(image)

    width, height = 2, 2
    content = [[None for _ in range(width)] for _ in range(height)]
    for i in range(height):
        for j in range(width):
            content[i][j] = Text(value=f"{i} {j}", fill="black", font="Roboto Medium Regular", size=30)

    table = Table(content=content, left_top=(10, 10))
    table.unite_cells((0, 0), (0, 1))
    # table.outline_width = 4
    # table.unite_cells((1,0), (1, 1))
    # table.unite_cells((0,0), (1, 1))
    # table.squeeze()
    table.pixels.padding = 1
    for i in range(height):
        for j in range(width):
            table[i][j].horizontal_alignment = "center"
            # table[i][j].pixels.padding = 4
    table[0][0].pixels.padding = 10
    # table[1][1].top_outline_width = 0
    # table[1][0].pixels.padding = 10
    table.draw(canvas)

    image.save("text_image.png")
    image.show()


if __name__ == "__main__":
    print(get_current_week_string_weekdays())
    print(get_current_week_string_days())

