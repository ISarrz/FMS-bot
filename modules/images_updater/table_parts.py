import os
from modules.images_updater.style import *
from PIL import Image, ImageDraw, ImageFont
from modules.files_api import fonts_path


def load_font(font, size):
    font_file = os.path.join(fonts_path, font) + ".ttf"
    loaded_font = ImageFont.truetype(font_file, size)
    return loaded_font


colors = {
    'white': '#FFFFFF',
    'black': '#000000',
    'red': '#FF0000',
    'gray': '#808080',
    "yellow": "#FFFF00",
    'discord1': '#424549',
    'discord2': '#36393e',
    'discord3': '#282b30',
    'discord4': '#1e2124'
}

header_font = load_font("Roboto Black", 60)
# header_font = load_font("Roboto Slab Bold", 60)
# header_font = load_font("Roboto Condensed Bold", 60)
header_text = TextStyle(header_font, color=colors['white'], alignment='center', spacing=0)
header_style = CellStyle(fill=colors['discord4'], padding=5, outline_color=colors['discord4'], line_width=14,
                         text_style=header_text)

class_font = load_font("Riffic Bold", 60)
class_text = TextStyle(class_font, color=colors['white'], alignment='center', spacing=0)
class_style = CellStyle(fill=colors['discord4'], padding=5, outline_color=colors['discord3'], line_width=14,
                        text_style=header_text)

date_font = load_font("Roboto Black", 50)
date_text = TextStyle(date_font, color=colors['white'], alignment='center', spacing=0)
date_style = CellStyle(fill=colors['discord4'], padding=10, outline_color=colors['discord4'], line_width=0,
                       text_style=date_text)

main_font = load_font("Roboto Bold", 34)
# main_font = load_font("Nunito Black", 34)
main_text = TextStyle(main_font, color=colors['white'], alignment='center', spacing=2)

main_style = CellStyle(fill=colors['discord1'], padding=10, outline_color=colors['discord3'], line_width=10,
                       text_style=main_text, minimum_height=150)

time_font = load_font("Roboto Bold", 34)
time_text = TextStyle(time_font, color=colors['discord1'], alignment='center', spacing=0)

time_style = CellStyle(fill=colors['discord4'], padding=2, outline_color=colors['discord4'], line_width=1,
                       text_style=time_text, minimum_height=150)

numbers_font = load_font("Roboto Black", 50)
numbers_text = TextStyle(numbers_font, color=colors['white'], alignment='center', spacing=0)

numbers_style = CellStyle(fill=colors['discord4'], padding=-30, outline_color=colors['discord4'], line_width=1,
                          text_style=numbers_text, minimum_height=150, minimum_width=10)

groups_font = load_font("Nunito Black", 40)
groups_text = TextStyle(groups_font, color=colors['white'], alignment='center', spacing=0)

groups_style = CellStyle(fill=colors['discord4'], padding=1, outline_color=colors['discord4'], line_width=0,
                         text_style=groups_text, minimum_height=20)

big_groups_font = load_font("Nunito Black", 40)
big_groups_text = TextStyle(big_groups_font, color=colors['white'], alignment='center', spacing=0)

big_groups_style = CellStyle(fill=colors['discord4'], padding=10, outline_color=colors['discord3'], line_width=10,
                             text_style=big_groups_text, minimum_height=20)

empty_font = load_font("Nunito Black", 1)
empty_text = TextStyle(empty_font, color=colors['white'], alignment='center', spacing=0)

empty_style = CellStyle(fill=colors['discord4'], padding=1, outline_color=colors['discord4'], line_width=0,
                        text_style=empty_text, minimum_height=1)

black_empty_font = load_font("Nunito Black", 1)
black_empty_text = TextStyle(black_empty_font, color=colors['white'], alignment='center', spacing=0)

black_empty_style = CellStyle(fill=colors['discord4'], padding=1, outline_color=colors['discord4'], line_width=0,
                              text_style=black_empty_text, minimum_height=1)

im = Image.new('RGB', (500, 500), colors['white'])
draw = ImageDraw.Draw(im)
