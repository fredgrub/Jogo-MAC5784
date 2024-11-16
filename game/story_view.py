import arcade
from arcade.gui import UIView, UIAnchorLayout, UITextArea, UIFlatButton, UIBoxLayout
from .configs import Configs


class StoryView(UIView):

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.GHOST_WHITE

        # Create an anchor layout to position widgets
        self.anchor = self.add_widget(UIAnchorLayout())

        self.anchor.add(
            UITextArea(
                text=Configs.STORY_TEXT,
                font_size=24,
                text_color=arcade.color.BLACK,
                size_hint=(1, 0.8),
            ),
            anchor_x="left",
            anchor_y="top",
            align_x=10,
            align_y=-10,
        )

        # Create a horizontal box layout for buttons
        h_box = UIBoxLayout(space_between=20, vertical=False)
        self.anchor.add(
            h_box, anchor_x="left", anchor_y="bottom", align_x=10, align_y=10
        )

        # Create a button to go back to the menu
        back_button = UIFlatButton(
            text="BACK",
            width=150,
        )

        # Create a button to start the game
        play_button = UIFlatButton(
            text="PLAY",
            width=150,
        )

        # Add buttons to horizontal box layout
        h_box.add(back_button)
        h_box.add(play_button)

        @play_button.event("on_click")
        def _(event):
            from .game_view import GameView

            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)

        @back_button.event("on_click")
        def _(event):
            from .menu_view import MenuView

            self.window.show_view(MenuView())
