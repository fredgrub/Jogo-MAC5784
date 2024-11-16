import arcade
from arcade.gui import (
    UIView,
    UIAnchorLayout,
    UIBoxLayout,
    UIFlatButton,
)
from .configs import Configs


class MenuView(UIView):

    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.GHOST_WHITE

        # Create an anchor layout to position widgets
        self.anchor = self.add_widget(UIAnchorLayout())

        # Create a vertical box layout for buttons
        v_box = UIBoxLayout(space_between=20)
        self.anchor.add(v_box, anchor_x="center", anchor_y="center")

        # Instantiate buttons
        start_button = UIFlatButton(text="START", width=150)
        quit_button = UIFlatButton(text="QUIT", width=150)

        # Create title using UILabel and add to vertical box layout
        v_box.add(
            arcade.gui.UILabel(
                text=Configs.SCREEN_TITLE,
                font_size=36,
                text_color=arcade.color.BLACK,
                align="center",
            )
        )

        # Add buttons to vertical box layout
        v_box.add(start_button)
        v_box.add(quit_button)

        @start_button.event("on_click")
        def _(event):
            from .story_view import StoryView

            self.window.show_view(StoryView())

        @quit_button.event("on_click")
        def _(event):
            self.window.close()
