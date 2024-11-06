import arcade
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from random import choice

@dataclass
class CropConfig:
    name: str
    seed_time: float
    sprout_time: float
    growing_time: float
    texture_prefix: str
    planting_cost: int
    harvest_reward: int

class CropType(Enum):
    CARROT = "carrot"
    POTATO = "potato"

CROP_CONFIGS = {
    CropType.CARROT: CropConfig(
        name="Carrot",
        seed_time=3.0,
        sprout_time=5.0,
        growing_time=7.0,
        texture_prefix="carrot",
        planting_cost=10,
        harvest_reward=25
    ),
    CropType.POTATO: CropConfig(
        name="Potato",
        seed_time=5.0,
        sprout_time=5.0,
        growing_time=5.0,
        texture_prefix="potato",
        planting_cost=15,
        harvest_reward=35
    )
}

class GameConstants:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 800
    SCREEN_TITLE = "Farm Game"
    GRID_SIZE = 5
    CELL_SIZE = 64
    PESTICIDE_COST = 40
    INITIAL_MAX_PESTS = 1
    CROPS_PER_NEW_PEST = 2
    

class Pest(arcade.Sprite):
    def __init__(self, preferred_crop: CropType, damage_per_second: float = 10):
        super().__init__("assets/pest.png")
        self.preferred_crop = preferred_crop
        self.base_damage = damage_per_second
        self.current_crop = None
    
    def get_damage_multiplier(self, game: 'FarmGame') -> float:
        adjacent_pests = self._count_adjacent_pests(game)
        # Multiplicador aumenta 25% por praga adjacente, até máximo de 2x
        return min(1 + (0.25 * adjacent_pests), 2.0)
        
    def _count_adjacent_pests(self, game: 'FarmGame') -> int:
        if not self.current_crop:
            return 0
            
        adjacent_positions = [
            (self.center_x + GameConstants.CELL_SIZE, self.center_y),
            (self.center_x - GameConstants.CELL_SIZE, self.center_y),
            (self.center_x, self.center_y + GameConstants.CELL_SIZE),
            (self.center_x, self.center_y - GameConstants.CELL_SIZE)
        ]
        
        count = 0
        for x, y in adjacent_positions:
            for pest in game.pests:
                if pest != self and pest.center_x == x and pest.center_y == y:
                    count += 1
        return count

    def update(self, delta_time: float, game: 'FarmGame'):
        if self.current_crop:
            damage_multiplier = self.get_damage_multiplier(game)
            self.current_crop.take_damage(self.base_damage * damage_multiplier * delta_time)
    
    def _find_adjacent_crops(self, game: 'FarmGame') -> List['Crop']:
        if not self.current_crop:
            return []
            
        adjacent_positions = [
            (self.center_x + GameConstants.CELL_SIZE, self.center_y),  # direita
            (self.center_x - GameConstants.CELL_SIZE, self.center_y),  # esquerda
            (self.center_x, self.center_y + GameConstants.CELL_SIZE),  # cima
            (self.center_x, self.center_y - GameConstants.CELL_SIZE)   # baixo
        ]
        
        valid_crops = []
        for x, y in adjacent_positions:
            crop = game._get_crop_at_coordinates(x, y)
            if crop and crop.crop_type == self.preferred_crop and crop.hp > 0:
                valid_crops.append(crop)
                
        return valid_crops

class Crop(arcade.Sprite):
    def __init__(self, crop_type: CropType, center_x: float, center_y: float, start_time: float):
        super().__init__()
        
        self.crop_type = crop_type
        self.config = CROP_CONFIGS[crop_type]
        self.growth_stage = 0
        self.start_time = start_time
        self.hp = 100
        self.cell_index = None
        
        # Load textures for different growth stages
        self.textures = [
            arcade.load_texture(f"assets/{self.config.texture_prefix}_{i}.png")
            for i in range(4)  # 4 growth stages
        ]
        
        self.texture = self.textures[0]
        self.center_x = center_x
        self.center_y = center_y

    def update(self, current_time: float):
        if self.growth_stage >= 3:  # Fully grown
            return
            
        time_elapsed = current_time - self.start_time
        required_time = self._get_stage_time()
        
        if time_elapsed >= required_time:
            self.growth_stage += 1
            self.texture = self.textures[self.growth_stage]
            self.start_time = current_time

    def _get_stage_time(self) -> float:
        if self.growth_stage == 0:
            return self.config.seed_time
        elif self.growth_stage == 1:
            return self.config.sprout_time
        return self.config.growing_time

    @property
    def growth_progress(self) -> float:
        if self.growth_stage >= 3:
            return 1.0
        time_elapsed = arcade.get_window().total_time - self.start_time
        return min(time_elapsed / self._get_stage_time(), 1.0)

    def can_harvest(self) -> bool:
        return self.growth_stage == 3 and self.hp > 0
    
    def take_damage(self, amount: float):
        self.hp = max(0, self.hp - amount)

class FarmGame(arcade.Window):
    def __init__(self):
        super().__init__(GameConstants.SCREEN_WIDTH, GameConstants.SCREEN_HEIGHT, GameConstants.SCREEN_TITLE)

        self._initialize_game()
    
    def _initialize_game(self):
        """Initialize/Reset all game state variables"""
        arcade.set_background_color(arcade.color.AMAZON)
        
        self.total_time = 0
        self.selected_crop = CropType.CARROT
        self.show_indicators = False
        
        self.terrain_sprites = arcade.SpriteList()
        self.crop_sprites = arcade.SpriteList()

        self.money = 100
        self.game_over = False
        
        # Create grid
        self.grid_positions = []
        self._setup_grid()
        self.dead_cells = set()

        self.pest_sprites = arcade.SpriteList()
        self.pests = []
        self.consumed_crops = 0
        self.pest_spawn_timer = 0
        self.pest_spawn_interval = 5


        self.selected_crop_text = arcade.Text(
            text=f"Selected (to change press 1 or 2): {CROP_CONFIGS[self.selected_crop].name}",
            x=10,
            y=GameConstants.SCREEN_HEIGHT - 30,
            color=arcade.color.WHITE,
            font_size=16
        )

        self.money_text = arcade.Text(
            text=f"Money: ${self.money}",
            x=10,
            y=GameConstants.SCREEN_HEIGHT - 60,
            color=arcade.color.YELLOW,
            font_size=16
        )

        self.cure_cost_text = arcade.Text(
            text=f"Pesticide Cost: ${GameConstants.PESTICIDE_COST}",
            x=10,
            y=GameConstants.SCREEN_HEIGHT - 90,
            color=arcade.color.LIGHT_GREEN,
            font_size=16
        )

        self.game_over_text = arcade.Text(
            text="Game Over. Click [ESC] to restart",
            x=GameConstants.SCREEN_WIDTH // 2,
            y=GameConstants.SCREEN_HEIGHT // 2,
            color=arcade.color.WHITE,
            font_size=24,
            anchor_x="center"
        )

        self.pests_info_text = arcade.Text(
            text="Pests: 0/1",
            x=10,
            y=GameConstants.SCREEN_HEIGHT - 120,
            color=arcade.color.RED,
            font_size=16
        )

    def _setup_grid(self):
        for row in range(GameConstants.GRID_SIZE):
            for col in range(GameConstants.GRID_SIZE):
                x = (col + 0.5) * GameConstants.CELL_SIZE
                y = (row + 0.5) * GameConstants.CELL_SIZE
                
                # Create and add terrain sprite
                terrain = arcade.Sprite(
                    "assets/terrain_alive.png",
                    center_x=x,
                    center_y=y
                )
                self.terrain_sprites.append(terrain)
                
                # Store grid position for later use
                self.grid_positions.append((x, y))

    def on_draw(self):
        self.clear()
    
        # Draw all sprites
        self.terrain_sprites.draw()
        self.crop_sprites.draw()
        self.pest_sprites.draw()
            
        if self.show_indicators:
            self._draw_indicators()
            
        self.selected_crop_text.draw()
        self.money_text.draw()
        self.cure_cost_text.draw()
        self.pests_info_text.draw()

        if self.game_over:
            self.game_over_text.draw()

    def on_update(self, delta_time: float):
        if self.game_over:
            return

        self.total_time += delta_time

        max_pests = GameConstants.INITIAL_MAX_PESTS + (self.consumed_crops // GameConstants.CROPS_PER_NEW_PEST)
        self.pests_info_text.text = f"Pests: {len(self.pests)}/{max_pests}"

        self.selected_crop_text.text = f"Selected (to change press 1 or 2): {CROP_CONFIGS[self.selected_crop].name}"
        self.money_text.text = f"Money: ${self.money}"

        if self.money <= 0:
            self.game_over = True
            return
        
        # Atualiza culturas
        for crop in self.crop_sprites:
            crop.update(self.total_time)
            if crop.hp <= 0:
                cell_idx = self._get_cell_index(crop.center_x, crop.center_y)
                if cell_idx is not None:
                    self.dead_cells.add(cell_idx)
                    self._update_terrain_texture(cell_idx, True)
                self.crop_sprites.remove(crop)
                self.consumed_crops += 1
        
        # Atualiza pragas existentes
        for pest in self.pests[:]:  # Usa uma cópia da lista para permitir remoção segura
            pest.update(delta_time, self)
            
            # Verifica se a cultura atual morreu ou não existe
            if not pest.current_crop or pest.current_crop.hp <= 0:
                adjacent_crops = pest._find_adjacent_crops(self)
                
                if adjacent_crops:
                    # Move para uma nova cultura adjacente
                    pest.current_crop = choice(adjacent_crops)
                    pest.center_x = pest.current_crop.center_x
                    pest.center_y = pest.current_crop.center_y
                else:
                    # Não há culturas adjacentes, então a praga morre
                    self.pest_sprites.remove(pest)
                    self.pests.remove(pest)
        
        # Tenta criar nova praga
        self.pest_spawn_timer += delta_time
        if self.pest_spawn_timer >= self.pest_spawn_interval:
            self._try_spawn_pest()
            self.pest_spawn_timer = 0
    
    def _update_terrain_texture(self, cell_idx: int, is_dead: bool):
        terrain_sprite = self.terrain_sprites[cell_idx]
        texture_name = "terrain_dead.png" if is_dead else "terrain_alive.png"
        terrain_sprite.texture = arcade.load_texture(f"assets/{texture_name}")
    
    def _try_spawn_pest(self):
        max_pests = GameConstants.INITIAL_MAX_PESTS + (self.consumed_crops // GameConstants.CROPS_PER_NEW_PEST)
        
        if len(self.pests) >= max_pests:
            return
            
        valid_crops = []
        
        # Se não há pragas, procura em qualquer lugar
        if not self.pests:
            valid_crops = [crop for crop in self.crop_sprites 
                        if crop.crop_type == CropType.CARROT and crop.hp > 0]
            # Spawna apenas uma praga inicial
            if valid_crops:
                self._spawn_single_pest(choice(valid_crops))
        else:
            # Procura culturas adjacentes a pragas existentes
            for pest in self.pests:
                adjacent_crops = self._get_valid_adjacent_crops(pest)
                valid_crops.extend([crop for crop in adjacent_crops 
                                if crop not in valid_crops])
            
            if valid_crops:
                self._spawn_single_pest(choice(valid_crops))

    def _get_valid_adjacent_crops(self, pest: Pest) -> List[Crop]:
        if not pest.current_crop:
            return []
            
        adjacent_positions = [
            (pest.center_x + GameConstants.CELL_SIZE, pest.center_y),
            (pest.center_x - GameConstants.CELL_SIZE, pest.center_y),
            (pest.center_x, pest.center_y + GameConstants.CELL_SIZE),
            (pest.center_x, pest.center_y - GameConstants.CELL_SIZE)
        ]
        
        valid_crops = []
        for x, y in adjacent_positions:
            crop = self._get_crop_at_coordinates(x, y)
            if (crop and 
                crop.crop_type == CropType.CARROT and 
                crop.hp > 0 and
                not any(p.current_crop == crop for p in self.pests)):
                valid_crops.append(crop)
        
        return valid_crops

    def _spawn_single_pest(self, target_crop: Crop):
        new_pest = Pest(CropType.CARROT)
        new_pest.center_x = target_crop.center_x
        new_pest.center_y = target_crop.center_y
        new_pest.current_crop = target_crop
        self.pest_sprites.append(new_pest)
        self.pests.append(new_pest)
    
    def _get_crop_at_coordinates(self, x: float, y: float) -> Optional[Crop]:
        for crop in self.crop_sprites:
            if crop.center_x == x and crop.center_y == y:
                return crop
        return None

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if self.game_over:
            return
    
        cell_idx = self._get_cell_index(x, y)
        if cell_idx is None:
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            # Check if there's already a crop at this position
            crop = self._get_crop_at_position(cell_idx)
            
            if not crop:
                self._plant_crop(cell_idx)
            # Verifica se a cultura pode ser colhida e não está sendo atacada pela praga
            elif crop.can_harvest() and not any(pest.current_crop == crop for pest in self.pests):
                self.money += CROP_CONFIGS[crop.crop_type].harvest_reward
                self.crop_sprites.remove(crop)
        
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self._try_cure_pest(cell_idx)
    
    def _try_cure_pest(self, cell_idx: int):
        crop = self._get_crop_at_position(cell_idx)
        if not crop:
            return
            
        # Procura por uma praga atacando esta cultura
        target_pest = None
        for pest in self.pests:
            if pest.current_crop == crop:
                target_pest = pest
                break
                
        if not target_pest:
            return
        
        # Remove a praga e deduz o custo
        self.money -= GameConstants.PESTICIDE_COST
        self.pest_sprites.remove(target_pest)
        self.pests.remove(target_pest)



    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE and self.game_over:
            self._initialize_game()
            return
            
        if self.game_over:
            return
        
        if symbol == arcade.key.SPACE:
            self.show_indicators = not self.show_indicators
        elif symbol == arcade.key.KEY_1:
            self.selected_crop = CropType.CARROT
        elif symbol == arcade.key.KEY_2:
            self.selected_crop = CropType.POTATO

    def _get_cell_index(self, x: float, y: float) -> Optional[int]:
        col = int(x // GameConstants.CELL_SIZE)
        row = int(y // GameConstants.CELL_SIZE)
        index = row * GameConstants.GRID_SIZE + col
        
        if 0 <= index < len(self.grid_positions):
            return index
        return None

    def _get_crop_at_position(self, cell_idx: int) -> Optional[Crop]:
        cell_x, cell_y = self.grid_positions[cell_idx]
        for crop in self.crop_sprites:
            if crop.center_x == cell_x and crop.center_y == cell_y:
                return crop
        return None

    def _plant_crop(self, cell_idx: int):
        if cell_idx in self.dead_cells:
            return
        
        # Verifica se o jogador tem dinheiro suficiente
        crop_cost = CROP_CONFIGS[self.selected_crop].planting_cost

        # Deduz o custo do plantio
        self.money -= crop_cost

        x, y = self.grid_positions[cell_idx]
        crop = Crop(self.selected_crop, x, y, self.total_time)
        self.crop_sprites.append(crop)

    def _draw_indicators(self):
        for crop in self.crop_sprites:
            hp_text = arcade.Text(
                text=f"HP: {int(crop.hp)}",
                x=crop.center_x - 20,
                y=crop.center_y + 20,
                color=arcade.color.WHITE,
                font_size=10
            )
            hp_text.draw()
            
            # Draw progress bar if not mature
            if crop.growth_stage < 3:
                progress = crop.growth_progress
                base_y = crop.center_y - 25
                
                arcade.draw_lbwh_rectangle_filled(
                    left=crop.center_x - 20,
                    bottom=crop.center_y - GameConstants.CELL_SIZE // 2,
                    width=40,
                    height=4,
                    color=arcade.color.BLACK
                )
                arcade.draw_lbwh_rectangle_filled(
                    left=crop.center_x - 20,
                    bottom=crop.center_y - GameConstants.CELL_SIZE // 2,
                    width=40 * progress,
                    height=4,
                    color=arcade.color.BABY_BLUE
                )
        # Desenha linhas entre pragas cooperando
        for pest in self.pests:
            multiplier = pest.get_damage_multiplier(self)
            if multiplier > 1.0:
                # Desenha linhas conectando pragas próximas
                adjacent_positions = [
                    (pest.center_x + GameConstants.CELL_SIZE, pest.center_y),
                    (pest.center_x - GameConstants.CELL_SIZE, pest.center_y),
                    (pest.center_x, pest.center_y + GameConstants.CELL_SIZE),
                    (pest.center_x, pest.center_y - GameConstants.CELL_SIZE)
                ]
                
                for x, y in adjacent_positions:
                    for other_pest in self.pests:
                        if other_pest != pest and other_pest.center_x == x and other_pest.center_y == y:
                            arcade.draw_line(
                                pest.center_x, pest.center_y,
                                other_pest.center_x, other_pest.center_y,
                                arcade.color.RED_ORANGE,
                                line_width=2
                            )
            
            # Mostra multiplicador de dano
            if multiplier > 1.0:
                damage_text = arcade.Text(
                    text=f"x{multiplier:.1f}",
                    x=pest.center_x - 15,
                    y=pest.center_y - 30,
                    color=arcade.color.RED_ORANGE,
                    font_size=10
                )
                damage_text.draw()


def main():
    game = FarmGame()
    arcade.run()

if __name__ == "__main__":
    main()