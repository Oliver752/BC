# level_editor.py
import pygame
import json
from settings import TILE_SIZE

class LevelEditor:
    def __init__(self):
        self.grid = []  # Level grid structure
        self.tile_types = ['empty', 'block', 'collectable', 'enemy']
        self.current_tile = 1  # Default to block

    def save_level(self, filename):
        # Save the level to a JSON file
        with open(filename, 'w') as file:
            json.dump(self.grid, file)

    def load_level(self, filename):
        # Load the level from a JSON file
        with open(filename, 'r') as file:
            self.grid = json.load(file)

    def draw_grid(self, screen):
        # Draw grid for editing
        for row_index, row in enumerate(self.grid):
            for col_index, tile in enumerate(row):
                x, y = col_index * TILE_SIZE, row_index * TILE_SIZE
                if tile == 1:
                    pygame.draw.rect(screen, (0, 128, 0), (x, y, TILE_SIZE, TILE_SIZE))  # Block
                elif tile == 2:
                    pygame.draw.circle(screen, (255, 223, 0), (x + TILE_SIZE // 2, y + TILE_SIZE // 2), TILE_SIZE // 4)  # Collectable
                elif tile == 3:
                    pygame.draw.rect(screen, (255, 0, 0), (x, y, TILE_SIZE, TILE_SIZE))  # Enemy
