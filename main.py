import arcade
import random

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Farm Simulator"

TILE_SIZE = 32
GRID_WIDTH = 20
GRID_HEIGHT = 15

class Tile:
    def __init__(self, x, y):
        self.sprite = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE, arcade.color.BUD_GREEN)
        self.sprite.center_x = x * TILE_SIZE + TILE_SIZE / 2
        self.sprite.center_y = y * TILE_SIZE + TILE_SIZE / 2
        self.crop = None
        self.x = x
        self.y = y

    def draw(self):
        # Draw the tile
        self.sprite.draw()
        # Draw the crop if it exists
        if self.crop:
            self.crop.draw()

class FarmGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Tile(x, y) for y in range(height)] for x in range(width)]
    
    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return None

    def get_all_tiles(self):
        return [tile for row in self.grid for tile in row]

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
            arcade.draw_circle_outline(self.center_x, self.center_y, TILE_SIZE // 4 + 2, arcade.color.RED, 2)

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
            self.texture = arcade.make_circle_texture(TILE_SIZE // 2, arcade.color.BROWN)
        elif self.growth_stage == 1:
            self.texture = arcade.make_circle_texture(TILE_SIZE // 2, arcade.color.DARK_GREEN)
        elif self.growth_stage == 2:
            self.texture = arcade.make_circle_texture(TILE_SIZE // 2, arcade.color.GREEN)
        elif self.growth_stage == 3:
            self.texture = arcade.make_circle_texture(TILE_SIZE // 2, arcade.color.APPLE_GREEN)
        elif self.growth_stage >= 4:
            self.texture = arcade.make_circle_texture(TILE_SIZE // 2, arcade.color.YELLOW_ORANGE)

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
            self.texture = arcade.make_circle_texture(TILE_SIZE // 2, arcade.color.BROWN)
        elif self.growth_stage == 1:
            self.texture = arcade.make_circle_texture(TILE_SIZE // 2, arcade.color.DARK_BROWN)
        elif self.growth_stage == 2:
            self.texture = arcade.make_circle_texture(TILE_SIZE // 2, arcade.color.LIGHT_BROWN)
        elif self.growth_stage >= 3:
            self.texture = arcade.make_circle_texture(TILE_SIZE // 2, arcade.color.BEIGE)

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
        min_distance = float('inf')
        nearest_tile = None
        for tile in farm_grid.get_all_tiles():
            if (isinstance(tile.crop, self.target_crop_type) and
                not tile.crop.infected):
                distance = abs(tile.x - self.x) + abs(tile.y - self.y)  # Manhattan distance
                if distance < min_distance:
                    min_distance = distance
                    nearest_tile = tile
        return nearest_tile

    def draw(self, farm_grid):
        tile = farm_grid.get_tile(self.x, self.y)
        if tile:
            screen_x, screen_y = tile.sprite.center_x, tile.sprite.center_y
            color = arcade.color.BLACK
            arcade.draw_rectangle_outline(screen_x, screen_y, TILE_SIZE, TILE_SIZE, color, 2)

class Player:
    def __init__(self):
        self.money = 100
        self.harvested_crops = 0
        self.selected_crop_type = CornCrop  # Default crop type
        self.crop_types = [CornCrop, SoybeanCrop]
        self.selected_action = 'harvest'  # Default action for right-click
        self.action_types = ['harvest', 'cure']

    def plant_crop(self, tile):
        if self.money >= 5 and not tile.crop:
            crop = self.selected_crop_type(tile.sprite.center_x, tile.sprite.center_y)
            tile.crop = crop
            self.money -= 5
            return True
        else:
            return False

    def harvest_crop(self, tile):
        if tile.crop and tile.crop.is_harvestable():
            tile.crop = None
            self.harvested_crops += 1
            self.money += 10
            return True
        else:
            return False

    def cure_crop(self, tile):
        cure_cost = 5  # Cost to cure an infected crop
        if tile.crop and tile.crop.infected:
            if self.money >= cure_cost:
                tile.crop.infected = False
                self.money -= cure_cost
                return True
            else:
                print("Not enough money to cure the crop.")
                return False
        else:
            return False

    def switch_action(self):
        current_index = self.action_types.index(self.selected_action)
        self.selected_action = self.action_types[(current_index + 1) % len(self.action_types)]

    def get_selected_action_name(self):
        return self.selected_action.capitalize()

    def get_selected_crop_name(self):
        if self.selected_crop_type == CornCrop:
            return "Corn"
        elif self.selected_crop_type == SoybeanCrop:
            return "Soybean"
        else:
            return "Unknown"

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
        self.pest = Pest(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), CornCrop)
        self.tile_list = [tile for row in self.farm_grid.grid for tile in row]
        self.setup_key_mappings()

    def setup_key_mappings(self):
        # Map keys to crop types
        self.crop_key_mapping = {
            arcade.key.C: CornCrop,
            arcade.key.S: SoybeanCrop
        }
        # Map keys to actions
        self.action_key_mapping = {
            arcade.key.H: 'harvest',
            arcade.key.R: 'cure'
        }

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
                print(f"{self.player.get_selected_crop_name()} planted at ({grid_x}, {grid_y})")
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            if self.player.selected_action == 'harvest':
                if self.player.harvest_crop(tile):
                    print(f"Crop harvested at ({grid_x}, {grid_y})")
            elif self.player.selected_action == 'cure':
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
        arcade.draw_text(f"Money: ${self.player.money}", 10, SCREEN_HEIGHT - 20, arcade.color.WHITE, 14)
        arcade.draw_text(f"Harvested Crops: {self.player.harvested_crops}", 10, SCREEN_HEIGHT - 40, arcade.color.WHITE, 14)
        arcade.draw_text(f"Turn: {self.current_turn}", 10, SCREEN_HEIGHT - 60, arcade.color.WHITE, 14)
        arcade.draw_text(f"Selected Crop: {self.player.get_selected_crop_name()}", 10, SCREEN_HEIGHT - 80, arcade.color.WHITE, 14)
        arcade.draw_text(f"Selected Action: {self.player.get_selected_action_name()}", 10, SCREEN_HEIGHT - 100, arcade.color.WHITE, 14)
        arcade.draw_text("Press 'C' for Corn, 'S' for Soybean", 10, SCREEN_HEIGHT - 120, arcade.color.WHITE, 12)
        arcade.draw_text("Press 'H' to Harvest, 'R' to Cure", 10, SCREEN_HEIGHT - 140, arcade.color.WHITE, 12)

    def draw_game_over(self):
        # Display Game Over message on the right side
        message = "Game Over!\nPress 'ESC' to restart."
        arcade.draw_text(message, SCREEN_WIDTH - 160, SCREEN_HEIGHT / 2, arcade.color.RED, 20, align="center", anchor_x="left", width=160)

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

def main():
    game = FarmingSimulator()
    arcade.run()

if __name__ == "__main__":
    main()
