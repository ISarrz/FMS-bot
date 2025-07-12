from PIL import ImageFont
from modules.config.paths import fonts_path
import os


def get_font(name):
    name = "_".join(name.split())
    path = os.path.join(fonts_path, name)
    return ImageFont.truetype(path)


BASE_FONT = get_font("Roboto Medium Regular")


class Text:
    _font: ImageFont
    _left_top: tuple[int, int]
    _right_bottom: tuple[int, int]

    def __init__(self, font=BASE_FONT, left_top=(0, 0), right_bottom=(0, 0)):
        self._font = font
        self._left_top = left_top
        self._right_bottom = right_bottom

    @property
    def width(self):
        return self.right_x - self.left_x

    @property
    def height(self):
        return self.bottom_y - self.top_y

    @property
    def left_x(self):
        return self._left_top[0]

    @property
    def top_y(self):
        return self._left_top[1]

    @property
    def right_x(self):
        return self._right_bottom[0]

    @property
    def bottom_y(self):
        return self._right_bottom[1]

    @property
    def left_top(self):
        return self._left_top

    @property
    def right_bottom(self):
        return self._right_bottom

    def draw(self, canvas):
        pass


from PIL import Image, ImageDraw, ImageFont

# Создаем пустое белое изображение
image = Image.new("RGB", (300, 100), color="white")

# Объект для рисования
draw = ImageDraw.Draw(image)

# Шрифт (по умолчанию или свой)
# font = ImageFont.load_default()  # или ImageFont.truetype("arial.ttf", size=20)
path = "/home/zero/PycharmProjects/FMS-bot/modules/data_updater/painter/fonts/Roboto.ttf"
font = ImageFont.truetype(path, size=20)

# Текст, координаты, цвет
draw.text((10, 30), "привет", fill="black", font=font)

# Сохраняем
image.save("text_image.png")
image.show()
