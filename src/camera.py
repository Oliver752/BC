import pygame
class Camera:
    def __init__(self, width, height, level_width, level_height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.level_width = level_width
        self.level_height = level_height

    def apply(self, entity):
        # Offset the entity based on camera position
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        # Center the camera on the player
        x = -target.rect.centerx + self.camera.width // 2
        y = -target.rect.centery + self.camera.height // 2

        # Clamp to boundaries
        x = max(-(self.level_width - self.camera.width), min(0, x))
        y = max(-(self.level_height - self.camera.height), min(0, y))

        self.camera = pygame.Rect(x, y, self.camera.width, self.camera.height)
