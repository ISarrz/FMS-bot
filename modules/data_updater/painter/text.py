from PIL import ImageFont
from modules.config.paths import fonts_path
from modules.data_updater.painter.pixels import Pixels
from modules.data_updater.painter.base_container import BaseContainer
import os
import dataclasses


def get_font(name, size=12):
    name = "_".join(name.split()) + ".ttf"
    path = os.path.join(fonts_path, name)
    return ImageFont.truetype(path, size=size)


BASE_FONT = get_font("Roboto Medium Regular", size=20)


class Text(BaseContainer):
    _value: str
    _font: ImageFont
    _fill: str

    def __init__(self, value="", fill="black", font=BASE_FONT, left_top=(0, 0)):
        self._font = font
        self._value = value
        self._fill = fill
        self.pixels = Pixels(container=self)

        self._update_pixels()
        self.pixels.left_top = left_top

    def _update_pixels(self):
        bbox = self._font.getbbox(self._value)
        width = bbox[2]
        height = bbox[3]

        self.pixels.width = width
        self.pixels.height = height

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def size(self):
        return self._font.size

    @size.setter
    def size(self, value):
        self._font = ImageFont.truetype(self._font.path, size=value)
        self._update_pixels()

    def draw(self, canvas):
        canvas.text(self.pixels.left_top, text=self._value, fill=self._fill, font=self._font)


if __name__ == "__main__":
    pass
    from PIL import Image, ImageDraw, ImageFont

    # Создаем пустое белое изображение
    image = Image.new("RGB", (300, 100), color="white")

    # Объект для рисования
    canvas = ImageDraw.Draw(image)

    left_top = (0, 0)
    fill_color = "black"

    text = Text(value="привет", fill=fill_color, left_top=left_top)
    text.size = 12
    print(text.pixels.center)
    print(text.size)
    text.draw(canvas)
    image.save("text_image.png")
    image.show()
