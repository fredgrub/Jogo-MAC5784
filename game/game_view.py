import arcade
import random
from arcade.gui import UIView, UIAnchorLayout, UIButtonRow, UILabel
from enum import Enum
from dataclasses import dataclass
from .configs import Configs
from typing import Optional, List, Set

CROP_HOTKEYS = {arcade.key.KEY_1: "carrot", arcade.key.KEY_2: "potato"}


class GrowthStage(Enum):
    SEEDLING = 0
    GROWING = 1
    MATURE = 2
    READY = 3

    @property
    def next_stage(self):
        try:
            return GrowthStage(self.value + 1)
        except ValueError:
            return self


class PlayerAction(Enum):
    PLANT = 0
    HARVEST = 1
    APPLY_PESTICIDE = 2


class PlagueState(Enum):
    SEARCHING = 0
    CONSUMING = 1
    DYING = 2


ACTION_HOTKEYS = {
    arcade.key.P: PlayerAction.PLANT,
    arcade.key.H: PlayerAction.HARVEST,
    arcade.key.X: PlayerAction.APPLY_PESTICIDE,
}


class Soil(arcade.Sprite):
    ALIVE = 0
    DEAD = 1

    _textures = None

    def __init__(self, center_x, center_y):
        super().__init__(center_x=center_x, center_y=center_y)

        if self._textures is None:
            raise RuntimeError(
                "Soil class must be initialized before creating instances."
            )

        for texture in self._textures:
            self.append_texture(texture)

        self.set_texture(self.ALIVE)

    def set_alive(self):
        self.set_texture(self.ALIVE)

    def set_dead(self):
        self.set_texture(self.DEAD)

    @property
    def is_alive(self):
        return self.texture == self.textures[self.ALIVE]

    def kill(self):
        self.set_texture(self.DEAD)


@dataclass
class CropConfig:
    crop_type: str
    growth_time: int
    value: int
    texture_paths: list[str]


class CropFactory:
    _crop_configs = {
        "carrot": CropConfig(
            crop_type="carrot",
            growth_time=5,
            value=20,
            texture_paths=[
                "assets/carrot_0.png",
                "assets/carrot_1.png",
                "assets/carrot_2.png",
                "assets/carrot_3.png",
            ],
        ),
        "potato": CropConfig(
            crop_type="potato",
            growth_time=6,
            value=25,
            texture_paths=[
                "assets/potato_0.png",
                "assets/potato_1.png",
                "assets/potato_2.png",
                "assets/potato_3.png",
            ],
        ),
    }

    @classmethod
    def create_crop(
        cls, crop_type: str, center_x: float, center_y: float, start_time: float
    ) -> "Crop":
        if crop_type not in cls._crop_configs:
            raise ValueError(f"Unknown crop type: {crop_type}")

        config = cls._crop_configs[crop_type]
        crop = Crop(center_x, center_y, start_time, config)
        # Garantir que o tipo da cultura está sendo definido
        crop.type = crop_type
        print(f"Created crop of type {crop_type} at ({center_x}, {center_y})")
        return crop


class Crop(arcade.Sprite):
    def __init__(
        self, center_x: float, center_y: float, start_time: float, config: CropConfig
    ):
        super().__init__(center_x=center_x, center_y=center_y)
        self.type = config.crop_type  # Armazenar o tipo da cultura
        self.growth_stage = GrowthStage.SEEDLING
        self.start_time = start_time
        self.hp = 100

        self.growth_time = config.growth_time
        self.value = config.value

        self._textures = [arcade.load_texture(path) for path in config.texture_paths]
        for texture in self._textures:
            self.append_texture(texture)

        self.update_texture()
        print(f"Initialized crop of type {self.type}")

    def update_texture(self):
        self.set_texture(self.growth_stage.value)

    def update(self, current_time):
        if self.growth_stage == GrowthStage.READY or self.hp <= 0:
            return

        time_elapsed = current_time - self.start_time
        if time_elapsed >= self.growth_time:
            self.growth_stage = self.growth_stage.next_stage
            self.update_texture()
            self.start_time = current_time

    def damage(self, amount):
        self.hp = max(0, self.hp - amount)

    @property
    def is_harvestable(self):
        return self.growth_stage == GrowthStage.READY


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.soil = None
        self.crop = None
        self.pest = None

    def create_soil(self, x, y, sprite_manager):
        self.soil = Soil(x, y)
        sprite_manager.add_soil(self.soil)


class SpriteManager:
    def __init__(self):
        self.soil_list = arcade.SpriteList(use_spatial_hash=True)
        self.crop_list = arcade.SpriteList(use_spatial_hash=True)
        self.pest_list = arcade.SpriteList()

        self.load_textures()

    def load_textures(self):
        Soil._textures = [
            arcade.load_texture("assets/terrain_alive.png"),
            arcade.load_texture("assets/terrain_dead.png"),
        ]

    def add_soil(self, soil):
        self.soil_list.append(soil)

    def add_crop(self, crop):
        self.crop_list.append(crop)

    def add_pest(self, pest):
        self.pest_list.append(pest)

    def remove_crop(self, crop):
        self.crop_list.remove(crop)

    def remove_pest(self, pest):
        self.pest_list.remove(pest)

    def draw(self):
        self.soil_list.draw()
        self.crop_list.draw()
        self.pest_list.draw()


class Grid:
    def __init__(self, num_rows, num_cols, sprite_manager):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.sprite_manager = sprite_manager

        start_x = (
            Configs.SCREEN_WIDTH - (num_cols * Configs.CELL_SIZE)
        ) // 2 + Configs.CELL_SIZE // 2
        start_y = (
            Configs.SCREEN_HEIGHT - (num_rows * Configs.CELL_SIZE)
        ) // 2 + Configs.CELL_SIZE // 2

        self.cells = []

        for row in range(num_rows):
            self.cells.append([])
            for col in range(num_cols):
                x = start_x + col * Configs.CELL_SIZE
                y = start_y + row * Configs.CELL_SIZE

                cell = Cell(x, y)
                cell.create_soil(x, y, self.sprite_manager)

                self.cells[row].append(cell)

    def get_cell(self, row, col):
        return self.cells[row][col]


class Player:

    def __init__(self):
        self.selected_action = PlayerAction.PLANT
        self.money = 250
        self.selected_crop_type = "carrot"

    def select_crop(self, crop_type: str):
        if crop_type in CropFactory._crop_configs:
            self.selected_crop_type = crop_type

    def select_action(self, action: PlayerAction):
        self.selected_action = action


class Plague(arcade.Sprite):
    def __init__(
        self, center_x: float, center_y: float, plague_manager: "PlagueManager"
    ):
        super().__init__("assets/pest.png", center_x=center_x, center_y=center_y)
        self.state = PlagueState.CONSUMING
        self.damage_per_second = 20
        self.target_crop = None
        self.plague_manager = plague_manager

    def update(self, delta_time: float):
        if self.state == PlagueState.CONSUMING and self.target_crop:
            # Calcular dano amplificado baseado em pragas adjacentes
            adjacent_plagues = self.get_adjacent_plagues()
            multiplier = min(1 + (len(adjacent_plagues) * 0.5), 3.0)
            damage = self.damage_per_second * delta_time * multiplier
            self.target_crop.damage(damage)

            # Se a cultura foi totalmente consumida
            if self.target_crop.hp <= 0:
                # Incrementar contador de culturas consumidas
                self.plague_manager.increment_crops_consumed()

                # Remover a cultura da célula atual
                current_cell = self.plague_manager._get_cell_for_position(
                    self.center_x, self.center_y
                )
                if current_cell:
                    self.plague_manager.grid.sprite_manager.remove_crop(
                        current_cell.crop
                    )
                    current_cell.crop = None
                    current_cell.soil.kill()

                # Procurar nova cultura alvo
                new_target = self.plague_manager._find_new_target(self)
                if new_target:
                    # Mover para nova cultura
                    self.target_crop = new_target
                    self.center_x = new_target.center_x
                    self.center_y = new_target.center_y
                else:
                    # Se não encontrar alvo, marcar para morrer
                    self.state = PlagueState.DYING

    def get_adjacent_plagues(self) -> List["Plague"]:
        if not self.target_crop:
            return []

        current_cell = self.plague_manager._get_cell_for_position(
            self.center_x, self.center_y
        )
        if not current_cell:
            return []

        adjacent_cells = self.plague_manager._get_adjacent_cells(current_cell)
        adjacent_plagues = []

        for cell in adjacent_cells:
            for plague in self.plague_manager.plagues:
                if (
                    plague is not self
                    and plague.target_crop
                    and plague.target_crop is cell.crop
                ):
                    adjacent_plagues.append(plague)

        return adjacent_plagues


class PlagueManager:
    def __init__(self, grid):
        self.grid = grid
        self.plagues: Set[Plague] = set()
        self.vulnerable_crop_types: Set[str] = set()
        self.plague_power = 1.0
        self.spawn_cooldown = 5.0
        self.time_since_spawn = self.spawn_cooldown
        self.max_plagues = 2
        self.crops_consumed = 0

        selected_crop = random.choice(list(CropFactory._crop_configs.keys()))
        self.vulnerable_crop_types = {selected_crop}
        print(f"Vulnerable crop type: {selected_crop}")

    def update(self, delta_time: float):
        self.time_since_spawn += delta_time

        self.update_max_plagues()

        if (
            len(self.plagues) < self.max_plagues
            and self.time_since_spawn >= self.spawn_cooldown
        ):
            print(f"Attempting to spawn plague. Current plagues: {len(self.plagues)}")
            self._try_spawn_plague()
            self.time_since_spawn = 0.0

        # Atualizar pragas existentes
        dead_plagues = set()
        for plague in self.plagues:
            plague.update(delta_time)
            if plague.state == PlagueState.DYING:
                dead_plagues.add(plague)

        # Remover pragas mortas
        for plague in dead_plagues:
            self.remove_plague(plague)

    def update_max_plagues(self):
        # Exemplo de fórmula para aumentar max_plagues
        # Começa com 2 e aumenta 1 a cada 2 plantas consumidas, até um máximo de 10
        new_max = min(2 + (self.crops_consumed // 2), 10)
        if new_max != self.max_plagues:
            self.max_plagues = new_max
            print(f"Max plagues increased to {self.max_plagues}")

    def increment_crops_consumed(self):
        self.crops_consumed += 1
        print(f"Crops consumed: {self.crops_consumed}")

    def _try_spawn_plague(self):
        vulnerable_crops = []
        for row in self.grid.cells:
            for cell in row:
                if (
                    cell.crop
                    and cell.crop.type in self.vulnerable_crop_types
                    and cell.crop.hp > 0
                    and not self._has_plague(cell)
                ):
                    vulnerable_crops.append(cell.crop)

        if vulnerable_crops:
            target_crop = random.choice(vulnerable_crops)
            print(
                f"Spawning plague on crop at ({target_crop.center_x}, {target_crop.center_y})"
            )
            new_plague = Plague(target_crop.center_x, target_crop.center_y, self)
            new_plague.target_crop = target_crop
            self.plagues.add(new_plague)
            self.grid.sprite_manager.add_pest(new_plague)
        else:
            print("No vulnerable crops found for new plague")

    def _find_new_target(self, plague: Plague) -> Optional[Crop]:
        current_cell = self._get_cell_for_position(plague.center_x, plague.center_y)
        if not current_cell:
            return None

        adjacent_cells = self._get_adjacent_cells(current_cell)
        valid_targets = []

        for cell in adjacent_cells:
            if (
                cell.crop
                and cell.crop.type in self.vulnerable_crop_types
                and cell.crop.hp > 0
                and not self._has_plague(cell)
            ):
                valid_targets.append(cell.crop)

        return random.choice(valid_targets) if valid_targets else None

    def remove_plague(self, plague: Plague):
        if plague in self.plagues:
            self.plagues.remove(plague)
            self.grid.sprite_manager.remove_pest(plague)

    def _has_plague(self, cell: Cell) -> bool:
        return any(plague.target_crop is cell.crop for plague in self.plagues)

    def _get_cell_for_position(self, x: float, y: float) -> Optional[Cell]:
        for row in self.grid.cells:
            for cell in row:
                if (
                    abs(cell.x - x) < Configs.CELL_SIZE / 2
                    and abs(cell.y - y) < Configs.CELL_SIZE / 2
                ):
                    return cell
        return None

    def _get_adjacent_cells(self, cell: Cell) -> List[Cell]:
        adjacent = []
        cell_pos = self._get_cell_indices(cell)
        if not cell_pos:
            return adjacent

        row, col = cell_pos
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < len(self.grid.cells) and 0 <= new_col < len(
                self.grid.cells[0]
            ):
                adjacent.append(self.grid.cells[new_row][new_col])

        return adjacent

    def _get_cell_indices(self, cell: Cell) -> Optional[tuple[int, int]]:
        for i, row in enumerate(self.grid.cells):
            for j, c in enumerate(row):
                if c is cell:
                    return (i, j)
        return None

    @property
    def active_plagues(self) -> int:
        return len(self.plagues)


class GameView(UIView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.AMAZON
        self.sprite_manager = SpriteManager()
        self.grid = None
        self.player = None
        self.total_time = None
        self.show_indicators = False

        self.root = self.add_widget(UIAnchorLayout())

    def setup(self):
        self.grid = Grid(Configs.GRID_ROWS, Configs.GRID_COLS, self.sprite_manager)
        self.player = Player()
        self.total_time = 0
        self.show_indicators = False

        self.crops_harvested = 0
        self.plagues_eliminated = 0

        self.plague_manager = PlagueManager(self.grid)

        # Menu esquerdo (dinheiro e informações de pragas)
        left_menu = UIButtonRow(vertical=True, size_hint=(0.3, 0.4))

        # Label do dinheiro
        self.money_label = UILabel(
            f"Money: {self.player.money}",
            font_size=24,
            size_hint=(1, 0.1),
            align="left",
        )
        left_menu.add(self.money_label)

        # Label das pragas
        self.plague_label = UILabel(
            f"Plagues: {self.plague_manager.active_plagues}/{self.plague_manager.max_plagues}",
            font_size=18,
            size_hint=(1, 0.1),
            align="left",
        )
        left_menu.add(self.plague_label)

        # Label das culturas vulneráveis
        self.vulnerable_crops_label = UILabel(
            f"Vulnerable Crops: {', '.join(self.plague_manager.vulnerable_crop_types)}",
            font_size=18,
            size_hint=(1, 0.1),
            align="left",
        )
        left_menu.add(self.vulnerable_crops_label)

        self.root.add(left_menu, anchor_x="left", anchor_y="top")

        # Menu direito (estatísticas)
        right_menu = UIButtonRow(vertical=True, size_hint=(0.3, 0.4))

        # Label de culturas colhidas
        self.harvested_label = UILabel(
            f"Crops Harvested: {self.crops_harvested}",
            font_size=18,
            size_hint=(1, 0.1),
            align="right",
        )
        right_menu.add(self.harvested_label)

        # Label de pragas eliminadas
        self.eliminated_label = UILabel(
            f"Plagues Eliminated: {self.plagues_eliminated}",
            font_size=18,
            size_hint=(1, 0.1),
            align="right",
        )
        right_menu.add(self.eliminated_label)

        self.root.add(right_menu, anchor_x="right", anchor_y="top")

        # Menu inferior (ações)
        bottom_menu = UIButtonRow(vertical=True, size_hint=(1, 0.1))
        self.action_label = UILabel(
            text=self._get_action_text(),
            font_size=20,
            width=400,
            align="center",
            text_color=arcade.color.GOLD,
        )
        bottom_menu.add(self.action_label)
        bottom_menu.add(
            UILabel(
                text="[P]lant | [H]arvest | [X] Pesticide | [1-2] Select Crop | [SPACE] Toggle Indicators",
                width=400,
                align="center",
            )
        )
        self.root.add(bottom_menu, anchor_x="center", anchor_y="bottom")

    def _get_action_text(self):
        action_texts = {
            PlayerAction.PLANT: f"Plant ({self.player.selected_crop_type})",
            PlayerAction.HARVEST: "Harvest",
            PlayerAction.APPLY_PESTICIDE: "Apply Pesticide",
        }

        return f"{action_texts[self.player.selected_action]}"

    def on_update(self, delta_time):
        self.total_time += delta_time

        self.plague_manager.update(delta_time)

        for crop in self.sprite_manager.crop_list:
            crop.update(self.total_time)

        self.money_label.text = f"Money: {self.player.money}"
        self.action_label.text = self._get_action_text()
        self.plague_label.text = f"Plagues: {self.plague_manager.active_plagues}/{self.plague_manager.max_plagues}"
        self.vulnerable_crops_label.text = (
            f"Vulnerable Crops: {', '.join(self.plague_manager.vulnerable_crop_types)}"
        )

        # Atualizar labels de estatísticas
        self.harvested_label.text = f"Crops Harvested: {self.crops_harvested}"
        self.eliminated_label.text = f"Plagues Eliminated: {self.plagues_eliminated}"

        # Verificar condição de game over
        if self.is_game_over():
            from .game_over_view import GameOverView

            self.window.show_view(
                GameOverView(
                    crops_harvested=self.crops_harvested,
                    plagues_eliminated=self.plagues_eliminated,
                )
            )

    def on_draw_before_ui(self):
        self.clear()
        self.sprite_manager.draw()

        if self.show_indicators:
            for crop in self.sprite_manager.crop_list:
                # Desenha a barra de HP
                hp_progress = crop.hp / 100

                # Barra de HP - fundo preto
                arcade.draw_lbwh_rectangle_filled(
                    left=crop.center_x - 20,
                    bottom=crop.center_y
                    - Configs.CELL_SIZE // 2
                    + 6,  # 6 pixels acima da barra de progresso
                    width=40,
                    height=4,
                    color=arcade.color.BLACK,
                )

                # Barra de HP - preenchimento verde/amarelo/vermelho dependendo do HP
                hp_color = (
                    arcade.color.GREEN
                    if hp_progress > 0.6
                    else arcade.color.YELLOW if hp_progress > 0.3 else arcade.color.RED
                )
                arcade.draw_lbwh_rectangle_filled(
                    left=crop.center_x - 20,
                    bottom=crop.center_y - Configs.CELL_SIZE // 2 + 6,
                    width=40 * hp_progress,
                    height=4,
                    color=hp_color,
                )

                # Desenha a barra de progresso apenas se não estiver pronta para colheita
                if crop.growth_stage != GrowthStage.READY:
                    # Barra de progresso de crescimento
                    time_elapsed = self.total_time - crop.start_time
                    growth_progress = min(time_elapsed / crop.growth_time, 1.0)

                    # Barra de progresso - fundo preto
                    arcade.draw_lbwh_rectangle_filled(
                        left=crop.center_x - 20,
                        bottom=crop.center_y - Configs.CELL_SIZE // 2,
                        width=40,
                        height=4,
                        color=arcade.color.BLACK,
                    )

                    # Barra de progresso - preenchimento azul
                    arcade.draw_lbwh_rectangle_filled(
                        left=crop.center_x - 20,
                        bottom=crop.center_y - Configs.CELL_SIZE // 2,
                        width=40 * growth_progress,
                        height=4,
                        color=arcade.color.BABY_BLUE,
                    )

            for plague in self.plague_manager.plagues:
                if plague.state == PlagueState.CONSUMING:
                    # Desenhar linhas entre pragas adjacentes
                    adjacent_plagues = plague.get_adjacent_plagues()
                    for adjacent_plague in adjacent_plagues:
                        arcade.draw_line(
                            plague.center_x,
                            plague.center_y,
                            adjacent_plague.center_x,
                            adjacent_plague.center_y,
                            arcade.color.RED,
                            2,  # espessura da linha
                        )

                    # Calcular e mostrar o multiplicador
                    multiplier = min(1 + (len(adjacent_plagues) * 0.5), 3.0)
                    if multiplier > 1.0:  # Só mostrar se houver boost
                        arcade.draw_text(
                            f"x{multiplier:.1f}",
                            plague.center_x - 15,
                            plague.center_y
                            - Configs.CELL_SIZE // 2
                            - 15,  # Posição abaixo da praga
                            arcade.color.RED,
                            12,  # tamanho da fonte
                            bold=True,
                        )

    def get_cell_from_position(self, x, y):
        start_x = (Configs.SCREEN_WIDTH - (self.grid.num_cols * Configs.CELL_SIZE)) // 2
        start_y = (
            Configs.SCREEN_HEIGHT - (self.grid.num_rows * Configs.CELL_SIZE)
        ) // 2

        col = int((x - start_x) // Configs.CELL_SIZE)
        row = int((y - start_y) // Configs.CELL_SIZE)

        if 0 <= row < self.grid.num_rows and 0 <= col < self.grid.num_cols:
            return self.grid.get_cell(row, col)
        return None

    def on_mouse_press(self, x, y, button, modifiers):
        cell = self.get_cell_from_position(x, y)
        if not cell or not cell.soil.is_alive:
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.player.selected_action == PlayerAction.PLANT:
                if cell.crop is None:
                    crop_config = CropFactory._crop_configs[
                        self.player.selected_crop_type
                    ]
                    if self.player.money >= crop_config.value:
                        new_crop = CropFactory.create_crop(
                            self.player.selected_crop_type,
                            cell.x,
                            cell.y,
                            self.total_time,
                        )
                        self.player.money -= crop_config.value
                        cell.crop = new_crop
                        self.sprite_manager.add_crop(new_crop)

                        # Verificar game over após gastar dinheiro
                        if self.is_game_over():
                            from .game_over_view import GameOverView

                            self.window.show_view(
                                GameOverView(
                                    crops_harvested=self.crops_harvested,
                                    plagues_eliminated=self.plagues_eliminated,
                                )
                            )

            elif self.player.selected_action == PlayerAction.HARVEST:
                has_plague = any(
                    plague.target_crop is cell.crop
                    for plague in self.plague_manager.plagues
                )

                if cell.crop and cell.crop.is_harvestable and not has_plague:
                    self.player.money += cell.crop.value
                    self.sprite_manager.remove_crop(cell.crop)
                    cell.crop = None
                    self.crops_harvested += 1

            elif self.player.selected_action == PlayerAction.APPLY_PESTICIDE:
                # Implementar lógica de pesticida
                cost = 30  # Custo do pesticida
                if self.player.money >= cost:
                    plagues_to_remove = [
                        plague
                        for plague in self.plague_manager.plagues
                        if plague.target_crop is cell.crop
                    ]
                    if plagues_to_remove:
                        self.player.money -= cost
                        for plague in plagues_to_remove:
                            self.plague_manager.remove_plague(plague)
                            self.plagues_eliminated += 1

    def on_key_press(self, key, modifiers):
        if key in CROP_HOTKEYS:
            self.player.select_crop(CROP_HOTKEYS[key])
            self.action_label.text = self._get_action_text()
        elif key in ACTION_HOTKEYS:
            self.player.select_action(ACTION_HOTKEYS[key])
            self.action_label.text = self._get_action_text()
        elif key == arcade.key.SPACE:
            self.show_indicators = not self.show_indicators

    def is_game_over(self) -> bool:
        # Verifica se há dinheiro suficiente para plantar a cultura mais barata
        cheapest_crop_cost = min(
            config.value for config in CropFactory._crop_configs.values()
        )
        has_money_to_plant = self.player.money >= cheapest_crop_cost

        # Verifica se há culturas que podem ser colhidas
        has_harvestable_crops = any(
            crop.is_harvestable for crop in self.sprite_manager.crop_list
        )

        # Verifica se há culturas crescendo
        has_growing_crops = any(
            not crop.is_harvestable for crop in self.sprite_manager.crop_list
        )

        # Verifica se há células vivas disponíveis para plantar
        has_available_cells = any(
            cell.soil.is_alive and cell.crop is None
            for row in self.grid.cells
            for cell in row
        )

        # Game over se:
        # 1. Não há dinheiro suficiente para plantar E
        # 2. Não há culturas para colher E
        # 3. Não há culturas crescendo
        # OU
        # 4. Não há células disponíveis para plantar E não há culturas no campo
        return (
            not has_money_to_plant
            and not has_harvestable_crops
            and not has_growing_crops
        ) or (
            not has_available_cells
            and not has_harvestable_crops
            and not has_growing_crops
        )
