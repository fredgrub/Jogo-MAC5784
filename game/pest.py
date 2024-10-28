import arcade
from game.constants import TILE_SIZE


class Pest:
    def __init__(self, x, y, target_crop_type):
        self.x = x
        self.y = y
        self.target_crop_type = target_crop_type

    def move(self, farm_grid):
        target_tile = self.find_nearest_target_crop(farm_grid)
        if target_tile:
            # Calculate direction towards target crop
            dx = target_tile.x - self.x
            dy = target_tile.y - self.y
            # Move one step in the direction
            if abs(dx) > abs(dy):
                self.x += 1 if dx > 0 else -1
            elif dy != 0:
                self.y += 1 if dy > 0 else -1
            # Ensure the pest stays within bounds
            self.x = max(0, min(self.x, farm_grid.width - 1))
            self.y = max(0, min(self.y, farm_grid.height - 1))
        # Infect the crop if there is one on the new tile
        tile = farm_grid.get_tile(self.x, self.y)
        if tile and tile.crop:
            tile.crop.infected = True

    def find_nearest_target_crop(self, farm_grid):
        min_distance = float("inf")
        nearest_tile = None
        for tile in farm_grid.get_all_tiles():
            if isinstance(tile.crop, self.target_crop_type) and not tile.crop.infected:
                distance = abs(tile.x - self.x) + abs(
                    tile.y - self.y
                )  # Manhattan distance
                if distance < min_distance:
                    min_distance = distance
                    nearest_tile = tile
        return nearest_tile

    def draw(self, farm_grid):
        tile = farm_grid.get_tile(self.x, self.y)
        if tile:
            screen_x, screen_y = tile.sprite.center_x, tile.sprite.center_y
            color = arcade.color.BLACK
            arcade.draw_rectangle_outline(
                screen_x, screen_y, TILE_SIZE, TILE_SIZE, color, 2
            )
