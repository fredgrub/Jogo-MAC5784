import arcade
import logging

from typing import List, Dict, Tuple

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Farmer Vs. Plague"

SPRITE_WIDTH = 64
SPRITE_HEIGHT = 64

ROW_COUNT = 20
COLUMN_COUNT = 20


class Crop:
    """Class to manage crop states and growth."""

    textures: List[arcade.Texture] = []

    @classmethod
    def load_textures(cls) -> None:
        cls.textures = [arcade.load_texture(f"assets/carrot_{i}.png") for i in range(4)]

    def __init__(self, sprite: arcade.Sprite, time_planted: float) -> None:
        self.sprite: arcade.Sprite = sprite
        self.growth_stage: int = 0
        self.time_planted: float = time_planted
        self.time_last_growth: float = time_planted

    def update(self, total_time: float) -> None:
        """Update the crop state based on the time passed."""
        if self.can_grow(total_time):
            self.grow()
            self.time_last_growth = total_time

    def grow(self) -> None:
        if self.growth_stage < len(self.textures) - 1:
            self.growth_stage += 1
            self.sprite.texture = self.textures[self.growth_stage]
            logging.info(f"Crop grew to stage {self.growth_stage}")

    def can_grow(self, current_time: float) -> bool:
        return current_time - self.time_last_growth > 5

    def is_fully_grown(self) -> bool:
        return self.growth_stage == len(self.textures) - 1


class Grid:
    """Class to manage the grid of terrain sprites."""

    def __init__(
        self, rows: int, columns: int, sprite_width: int, sprite_height: int
    ) -> None:
        self.rows: int = rows
        self.columns: int = columns
        self.sprite_width: int = sprite_width
        self.sprite_height: int = sprite_height

        self.grid_spritelist: arcade.SpriteList = arcade.SpriteList()
        self.grid_sprites: List[List[arcade.Sprite]] = []

        self.create_grid_sprites()

    def create_grid_sprites(self) -> None:
        for row in range(self.rows):
            row_sprites: List[arcade.Sprite] = []
            for column in range(self.columns):
                sprite = arcade.Sprite("assets/terrain_alive.png")
                sprite.center_x = column * self.sprite_width + self.sprite_width // 2
                sprite.center_y = row * self.sprite_height + self.sprite_height // 2
                self.grid_spritelist.append(sprite)
                row_sprites.append(sprite)
            self.grid_sprites.append(row_sprites)


class CropManager:
    """Class to manage all crops."""

    def __init__(self) -> None:
        self.active_crops: arcade.SpriteList = arcade.SpriteList()
        self.crops: List[Crop] = []
        self.crop_grid: Dict[Tuple[int, int], Crop] = {}

    def add_crop(self, crop: Crop, row: int, column: int) -> None:
        self.crops.append(crop)
        self.active_crops.append(crop.sprite)
        self.crop_grid[(row, column)] = crop

    def remove_crop(self, crop: Crop, row: int, column: int) -> None:
        self.crops.remove(crop)
        self.active_crops.remove(crop.sprite)
        del self.crop_grid[(row, column)]

    def update_crops(self, total_time: float) -> None:
        for crop in self.crops:
            crop.update(total_time)


class GameView(arcade.View):
    """Main application class."""

    def __init__(self) -> None:
        super().__init__()

        # Set the background color of the window
        arcade.set_background_color(arcade.color.AMAZON)

        self.grid: Grid = Grid(ROW_COUNT, COLUMN_COUNT, SPRITE_WIDTH, SPRITE_HEIGHT)
        self.crop_manager: CropManager = CropManager()

        Crop.load_textures()

        # Create the camera for the sprites
        self.camera_sprites: arcade.Camera2D = arcade.Camera2D()

        self.total_time: float = 0.0

    def on_update(self, delta_time: float) -> None:
        """Update the game."""
        self.total_time += delta_time
        self.crop_manager.update_crops(self.total_time)

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear()
        self.camera_sprites.use()
        self.grid.grid_spritelist.draw()
        self.crop_manager.active_crops.draw()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        """Called when the user presses a mouse button."""
        if button == arcade.MOUSE_BUTTON_LEFT:
            world_point = self.camera_sprites.unproject((x, y))
            column = int(world_point.x // SPRITE_WIDTH)
            row = int(world_point.y // SPRITE_HEIGHT)

            if 0 <= row < ROW_COUNT and 0 <= column < COLUMN_COUNT:
                logging.info(
                    f"Click at screen ({x}, {y}), world ({int(world_point.x)}, {int(world_point.y)}), grid ({row}, {column})"
                )

                if (row, column) not in self.crop_manager.crop_grid:
                    crop_sprite = arcade.Sprite()
                    crop_sprite.texture = Crop.textures[0]
                    crop_sprite.center_x = column * SPRITE_WIDTH + SPRITE_WIDTH // 2
                    crop_sprite.center_y = row * SPRITE_HEIGHT + SPRITE_HEIGHT // 2

                    new_crop = Crop(crop_sprite, self.total_time)
                    self.crop_manager.add_crop(new_crop, row, column)
                    logging.info(f"Crop planted at ({row}, {column})")
                else:
                    crop = self.crop_manager.crop_grid[(row, column)]
                    if crop.is_fully_grown():
                        self.crop_manager.remove_crop(crop, row, column)
                        logging.info(f"Crop harvested from ({row}, {column})")

    def on_mouse_drag(
        self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int
    ) -> None:
        """Called when the user moves the mouse with a button pressed."""
        if buttons == arcade.MOUSE_BUTTON_RIGHT:
            self.camera_sprites.position = (
                self.camera_sprites.position[0] - dx,
                self.camera_sprites.position[1] - dy,
            )


def main() -> None:
    """Main function"""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    main()
