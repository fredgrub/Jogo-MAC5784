from arcade import Window
from .configs import Configs
from .menu_view import MenuView


class MyGame:

    def __init__(self):
        self.window = Window(
            Configs.SCREEN_WIDTH,
            Configs.SCREEN_HEIGHT,
            Configs.SCREEN_TITLE,
        )

    def start(self):
        self.window.show_view(MenuView())
        self.window.run()
