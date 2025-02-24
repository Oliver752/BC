# blocks.py
import pygame
from settings import TILE_SIZE

# Load block textures
BLOCK_TEXTURES = {
    'grass': pygame.image.load('assets/images/blocks/grass.png'),
    'dirt': pygame.image.load('assets/images/blocks/dirt.png'),
    'stone': pygame.image.load('assets/images/blocks/stone.png'),
}

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type='grass'):
        super().__init__()
        # Assign texture based on type
        self.image = BLOCK_TEXTURES.get(block_type, BLOCK_TEXTURES['grass'])
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.block_type = block_type
