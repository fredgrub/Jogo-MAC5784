from game.tile import Tile


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
