from dataclasses import dataclass, field


@dataclass
class Pixel:
    x: int = 0
    y: int = 0
    width: int = 20
    height: int = 20


@dataclass
class Padding:
    # pixels
    vertical: int = 2
    horizontal: int = 2


@dataclass
class Layout:
    padding: Padding = field(default_factory=Padding)
    horizontal_gap: int = 2


@dataclass
class Alignment:
    vertical: str
    horizontal: int


@dataclass
class Text:
    _value: str
    pixel: Pixel = field(default_factory=Pixel)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


@dataclass
class Container:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    layout: Layout = field(default_factory=Layout)
    content: list = field(default_factory=list)


text = Text('1')
print(text.value)
pass
