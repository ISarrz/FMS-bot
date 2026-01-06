from modules.data_updater.painter.containers.pixels import Pixels
from modules.data_updater.painter.containers.simple_container import SimpleContainer


class BaseContainer(SimpleContainer):
    pixels: Pixels

    def draw(self, canvas):
        pass
