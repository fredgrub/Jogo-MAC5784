import arcade
from game.constants import TILE_SIZE


class Crop(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.growth_percent = 0
        self.hp = 100
        self.infected = False

    def grow(self, growth_rate):
        """Increase growth percent by growth_rate each turn until 100%."""
        if self.hp > 0 and self.growth_percent < 100:
            self.growth_percent = min(self.growth_percent + growth_rate, 100)
            self.update_texture()

    def take_damage(self, damage):
        """Apply damage to crop, decreasing HP."""
        self.hp = max(self.hp - damage, 0)

    def is_harvestable(self):
        """Check if the crop can be harvested."""
        return not self.infected and self.growth_percent == 100 and self.hp > 0

    def draw(self):
        super().draw()
        if self.infected:
            arcade.draw_circle_outline(
                self.center_x, self.center_y, TILE_SIZE // 4 + 2, arcade.color.RED, 2
            )

    def update_texture(self):
        """To be implemented by subclasses to reflect growth stages."""
        pass


class CornCrop(Crop):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.growth_rate = 15  # Growth rate per turn for corn
        self.update_texture()

    def grow(self):
        super().grow(self.growth_rate)  # Use base class grow with growth_rate

    def update_texture(self):
        """Update texture based on growth percentage."""
        if self.growth_percent < 25:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.BROWN
            )
        elif self.growth_percent < 50:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.DARK_GREEN
            )
        elif self.growth_percent < 75:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.GREEN
            )
        elif self.growth_percent < 100:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.APPLE_GREEN
            )
        else:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.YELLOW_ORANGE
            )


class SoybeanCrop(Crop):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.growth_rate = 20  # Growth rate per turn for soybeans
        self.update_texture()

    def grow(self):
        super().grow(self.growth_rate)  # Use base class grow with growth_rate

    def update_texture(self):
        """Update texture based on growth percentage."""
        if self.growth_percent < 33:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.BROWN
            )
        elif self.growth_percent < 66:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.DARK_BROWN
            )
        elif self.growth_percent < 100:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.LIGHT_BROWN
            )
        else:
            self.texture = arcade.make_circle_texture(
                TILE_SIZE // 2, arcade.color.BEIGE
            )
