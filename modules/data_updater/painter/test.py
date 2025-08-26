from typing import List
from PIL import ImageFont, ImageDraw, Image
from modules.data_updater.painter.table import Table
from modules.data_updater.painter.column import Column
from modules.data_updater.painter.text import Text

def table():
    image = Image.new('RGB', (500, 500), "white")
    canvas = ImageDraw.Draw(image)
    width = 2
    height = 2
    content = [[None for i in range(width)] for j in range(height)]
    for i in range(height):
        for j in range(width):
            content[i][j] = Text(value=str(i) + " " + str(j), fill="black")
            content[i][j].size = 30

    column = Column(left_top=(10, 10), outline_size=0)
    text1 = Text(value="Hello, world!")
    text1._fill = "#FFFFFF"
    text2 = Text(value="Hello!")
    text1.size = 50
    text2.size = 40
    text2._fill = "#FFFFFF"
    column.add(text1)
    column.add(text2)

    content[0][0] = column

    # column.draw(canvas)

    left_top = (10, 10)
    table = Table(left_top=left_top, content=content)
    table.pixels.padding = 10
    table.unite_cells((0,0), (0, 1))
    table.squeeze()

    table[0][0].fill = "#424549"


    # table._content[0][0].draw(canvas)
    # table._content[0][0]._content.draw(canvas)
    table.draw(canvas)
    # table

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

table()