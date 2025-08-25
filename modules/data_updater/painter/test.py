from PIL import Image, ImageDraw, ImageFont
from PIL import ImageFont
from modules.config.paths import fonts_path
from modules.data_updater.painter.pixels import Pixels
from modules.data_updater.painter.base_container import BaseContainer
import os
import dataclasses
# создаём изображение
img = Image.new("RGB", (400, 200), "white")
draw = ImageDraw.Draw(img)


def get_font(name, size=12):
    name = "_".join(name.split()) + ".ttf"
    path = os.path.join(fonts_path, name)
    return ImageFont.truetype(path, size=size)


font = get_font("Roboto Medium Regular", 30)


# текст и координаты привязки
text = "Hello!i"
x, y = 50, 100  # точка привязки (baseline)
draw.text((x, y), text, font=font, fill="black")

# вычисляем bbox
bbox = draw.textbbox((x, y), text, font=font)  # (left, top, right, bottom)

# рисуем bbox красным
draw.rectangle(bbox, outline="red", width=2)

# рисуем точку привязки зелёным крестиком
cross_size = 5
draw.line((x-cross_size, y, x+cross_size, y), fill="green", width=2)
draw.line((x, y-cross_size, x, y+cross_size), fill="green", width=2)

img.show()
