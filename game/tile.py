import arcade
from game.constants import TILE_SIZE


class Tile:
    """Represents a tile in the game grid."""

    def __init__(self, x, y):
        """
        Initializes the Tile object with position (x, y) in the grid.

        Args:
            x (int): The x position in the grid.
            y (int): The y position in the grid.
        """
        self.x = x
        self.y = y
        self.sprite = self._create_sprite()
        self.crop = None

    def _create_sprite(self):
        """Creates and positions the sprite for the tile."""
        sprite = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE, arcade.color.BUD_GREEN)
        sprite.center_x = self.x * TILE_SIZE + TILE_SIZE / 2
        sprite.center_y = self.y * TILE_SIZE + TILE_SIZE / 2
        return sprite

    def draw(self):
        """Draws the tile and any crop overlay if present."""
        self.sprite.draw()
        if self.crop:
            self.crop.draw()
