import arcade
from arcade.gui import (
    UIView,
    UIAnchorLayout,
    UIBoxLayout,
    UIFlatButton,
)


class GameOverView(UIView):
    def __init__(self, crops_harvested=0, plagues_eliminated=0):
        super().__init__()
        self.background_color = arcade.color.GHOST_WHITE
        self.crops_harvested = crops_harvested
        self.plagues_eliminated = plagues_eliminated

        # Create an anchor layout to position widgets
        self.anchor = self.add_widget(UIAnchorLayout())

        # Create a vertical box layout for buttons
        v_box = UIBoxLayout(space_between=20)
        self.anchor.add(v_box, anchor_x="center", anchor_y="center")

        # Instantiate buttons
        restart_button = UIFlatButton(text="RESTART", width=150)
        quit_button = UIFlatButton(text="QUIT", width=150)

        # Create title using UILabel and add to vertical box layout
        v_box.add(
            arcade.gui.UILabel(
                text="GAME OVER :(",
                font_size=36,
                text_color=arcade.color.BLACK,
                align="center",
            )
        )

        # Add stats
        v_box.add(
            arcade.gui.UILabel(
                text=f"Crops Harvested: {self.crops_harvested}",
                font_size=18,
                text_color=arcade.color.BLACK,
                align="center",
            )
        )

        v_box.add(
            arcade.gui.UILabel(
                text=f"Plagues Eliminated: {self.plagues_eliminated}",
                font_size=18,
                text_color=arcade.color.BLACK,
                align="center",
            )
        )

        # Add buttons to vertical box layout
        v_box.add(restart_button)
        v_box.add(quit_button)

        @restart_button.event("on_click")
        def _(event):
            from .game_view import GameView

            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)

        @quit_button.event("on_click")
        def _(event):
            self.window.close()
