import dataclasses

from PIL import ImageFont


@dataclasses.dataclass
class TextStyle:
    font: ImageFont
    color: str = '#000000'
    alignment: str = 'center'
    spacing: int = 2


@dataclasses.dataclass
class CellStyle:
    text_style: TextStyle
    fill: str = '#FFFFFF'
    padding: int = 5
    minimum_height: int = 10
    minimum_width: int = 10
    top_padding: int = 5
    outline_color: str = '#000000'
    line_width: int = 4
