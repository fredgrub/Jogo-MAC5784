import arcade
import random
from game.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    GRID_HEIGHT,
    GRID_WIDTH,
    TILE_SIZE,
)
from game.grid import FarmGrid
from game.player import Player
from game.pest import Pest
from game.crop import CornCrop, SoybeanCrop


class FarmingSimulator(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.restart_game()

    def restart_game(self):
        self.farm_grid = FarmGrid(GRID_WIDTH, GRID_HEIGHT)
        self.player = Player()
        self.current_turn = 1
        self.game_over = False
        # Pest prefers CornCrop by default
        self.pest = Pest(
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1),
            CornCrop,
        )
        self.tile_list = [tile for row in self.farm_grid.grid for tile in row]
        self.setup_key_mappings()

    def setup_key_mappings(self):
        # Map keys to crop types
        self.crop_key_mapping = {arcade.key.C: CornCrop, arcade.key.S: SoybeanCrop}
        # Map keys to actions
        self.action_key_mapping = {arcade.key.H: "harvest", arcade.key.R: "cure"}

    def on_draw(self):
        arcade.start_render()
        for tile in self.tile_list:
            tile.draw()
        self.draw_ui()
        if not self.game_over:
            self.pest.draw(self.farm_grid)
        else:
            self.draw_game_over()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over:
            return  # Ignore inputs if game is over

        grid_x = int(x // TILE_SIZE)
        grid_y = int(y // TILE_SIZE)
        tile = self.farm_grid.get_tile(grid_x, grid_y)

        if not tile:
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.player.plant_crop(tile):
                print(
                    f"{self.player.get_selected_crop_name()} planted at ({grid_x}, {grid_y})"
                )
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            if self.player.selected_action == "harvest":
                if self.player.harvest_crop(tile):
                    print(f"Crop harvested at ({grid_x}, {grid_y})")
            elif self.player.selected_action == "cure":
                if self.player.cure_crop(tile):
                    print(f"Crop cured at ({grid_x}, {grid_y})")
                else:
                    print(f"Failed to cure crop at ({grid_x}, {grid_y})")

        self.check_game_over()
        if not self.game_over:
            self.end_turn()

    def on_key_press(self, key, modifiers):
        if self.game_over:
            if key == arcade.key.ESCAPE:
                self.restart_game()
        else:
            if key in self.crop_key_mapping:
                self.player.selected_crop_type = self.crop_key_mapping[key]
                print(f"Selected crop: {self.player.get_selected_crop_name()}")
            elif key in self.action_key_mapping:
                self.player.selected_action = self.action_key_mapping[key]
                print(f"Selected action: {self.player.get_selected_action_name()}")

    def draw_ui(self):
        # Left side UI
        arcade.draw_text(
            f"Money: ${self.player.money}",
            10,
            SCREEN_HEIGHT - 20,
            arcade.color.WHITE,
            14,
        )
        arcade.draw_text(
            f"Harvested Crops: {self.player.harvested_crops}",
            10,
            SCREEN_HEIGHT - 40,
            arcade.color.WHITE,
            14,
        )
        arcade.draw_text(
            f"Turn: {self.current_turn}", 10, SCREEN_HEIGHT - 60, arcade.color.WHITE, 14
        )
        arcade.draw_text(
            f"Selected Crop: {self.player.get_selected_crop_name()}",
            10,
            SCREEN_HEIGHT - 80,
            arcade.color.WHITE,
            14,
        )
        arcade.draw_text(
            f"Selected Action: {self.player.get_selected_action_name()}",
            10,
            SCREEN_HEIGHT - 100,
            arcade.color.WHITE,
            14,
        )
        arcade.draw_text(
            "Press 'C' for Corn, 'S' for Soybean",
            10,
            SCREEN_HEIGHT - 120,
            arcade.color.WHITE,
            12,
        )
        arcade.draw_text(
            "Press 'H' to Harvest, 'R' to Cure",
            10,
            SCREEN_HEIGHT - 140,
            arcade.color.WHITE,
            12,
        )

    def draw_game_over(self):
        # Display Game Over message on the right side
        message = "Game Over!\nPress 'ESC' to restart."
        arcade.draw_text(
            message,
            SCREEN_WIDTH - 160,
            SCREEN_HEIGHT / 2,
            arcade.color.RED,
            20,
            align="center",
            anchor_x="left",
            width=160,
        )

    def check_game_over(self):
        if self.player.money <= 0:
            self.game_over = True
            print("Game Over!")

    def end_turn(self):
        self.current_turn += 1
        self.grow_crops()
        self.pest.move(self.farm_grid)

    def grow_crops(self):
        for tile in self.tile_list:
            if tile.crop:
                tile.crop.grow()

    def update(self, delta_time):
        # Optional: Implement if you want automatic game updates
        pass
