# collectables.py
import pygame
from settings import TILE_SIZE

class Collectable(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load the coin image
        self.image = pygame.image.load("assets/images/collectables/coin.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE // 2, TILE_SIZE // 2))
        self.rect = self.image.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))

    def update(self):
        # Collectables currently do not have behavior, but we can add animations later
        pass
