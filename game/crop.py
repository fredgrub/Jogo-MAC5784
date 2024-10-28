import arcade
from game.constants import TILE_SIZE


class Crop(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.state = "newly_planted"
        self.growth_stage = 0
        self.infected = False

    def grow(self):
        pass  # To be implemented by subclasses

    def is_harvestable(self):
        return self.state == "mature" and not self.infected

    def draw(self):
        super().draw()
        if self.infected:
            arcade.draw_circle_outline(
                self.center_x, self.center_y, TILE_SIZE // 4 + 2, arcade.color.RED, 2
            )


class CornCrop(Crop):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_growth_stage = 4
        self.update_texture()

    def grow(self):
        self.growth_stage += 1
        self.update_texture()
        if self.growth_stage >= self.max_growth_stage:
            self.state = "mature"

    def update_texture(self):
        # Update texture based on growth stage
        if self.growth_stage == 0:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.BROWN
            )
        elif self.growth_stage == 1:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.DARK_GREEN
            )
        elif self.growth_stage == 2:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.GREEN
            )
        elif self.growth_stage == 3:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.APPLE_GREEN
            )
        elif self.growth_stage >= 4:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.YELLOW_ORANGE
            )


class SoybeanCrop(Crop):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_growth_stage = 3
        self.update_texture()

    def grow(self):
        self.growth_stage += 1
        self.update_texture()
        if self.growth_stage >= self.max_growth_stage:
            self.state = "mature"

    def update_texture(self):
        # Update texture based on growth stage
        if self.growth_stage == 0:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.BROWN
            )
        elif self.growth_stage == 1:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.DARK_BROWN
            )
        elif self.growth_stage == 2:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.LIGHT_BROWN
            )
        elif self.growth_stage >= 3:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.BEIGE
            )
