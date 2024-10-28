from game.crop import CornCrop, SoybeanCrop


class Player:
    def __init__(self):
        self.money = 100
        self.harvested_crops = 0
        self.selected_crop_type = CornCrop  # Default crop type
        self.crop_types = [CornCrop, SoybeanCrop]
        self.selected_action = "harvest"  # Default action for right-click
        self.action_types = ["harvest", "cure"]

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
        self.selected_action = self.action_types[
            (current_index + 1) % len(self.action_types)
        ]

    def get_selected_action_name(self):
        return self.selected_action.capitalize()

    def get_selected_crop_name(self):
        if self.selected_crop_type == CornCrop:
            return "Corn"
        elif self.selected_crop_type == SoybeanCrop:
            return "Soybean"
        else:
            return "Unknown"
