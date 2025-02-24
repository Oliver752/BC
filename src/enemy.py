# enemy.py
import pygame
from settings import TILE_SIZE

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Enemy block design (can be animated later)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((255, 0, 0))  # Red color for enemies
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1  # Moving direction (1 = right, -1 = left)
        self.speed = 2

    def update(self):
        # Move the enemy horizontally
        self.rect.x += self.direction * self.speed

        # Change direction when hitting boundaries (can add collision detection later)
        if self.rect.left < 0 or self.rect.right > TILE_SIZE * 10:  # Example boundary
            self.direction *= -1