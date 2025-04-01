import pygame
from settings import TILE_SIZE

BLOCK_TEXTURES = {
    'grass': pygame.image.load('assets/images/blocks/grass.png'),
    'dirt': pygame.image.load('assets/images/blocks/dirt.png'),
    'stone': pygame.image.load('assets/images/blocks/stone.png'),
    'sand': pygame.image.load('assets/images/blocks/sand.png'),
    'sand2': pygame.image.load('assets/images/blocks/sand2.png'),
    'snow': pygame.image.load('assets/images/blocks/snow.png'),
    'snow2': pygame.image.load('assets/images/blocks/snow2.png'),
    'purple': pygame.image.load('assets/images/blocks/purple.png'),
    'purple2': pygame.image.load('assets/images/blocks/purple2.png'),
    'dirt2': pygame.image.load('assets/images/blocks/dirt2.png'),
    'dirt3': pygame.image.load('assets/images/blocks/dirt3.png'),
    'floor': pygame.image.load('assets/images/blocks/floor.png'),
}
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, block_type='grass'):
        super().__init__()
        self.image = BLOCK_TEXTURES.get(block_type, BLOCK_TEXTURES['grass'])
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.block_type = block_type
