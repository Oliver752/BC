import pygame
from settings import TILE_SIZE

class Collectable(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        target_width = TILE_SIZE // 2
        target_height = int(target_width * 12 / 14)

        self.animations = {
            "idle": self.load_animation("assets/images/collectables/diamond_idle.png", 12, 10, 10, scale=(target_width, target_height)),
            "disappear": self.load_animation("assets/images/collectables/diamond_disappear.png", 12, 10, 2, scale=(target_width, target_height))
        }
        self.state = "idle"
        self.frame_index = 0
        self.frame_duration = 100
        self.last_update = pygame.time.get_ticks()

        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))

        self.sound = pygame.mixer.Sound("assets/sounds/other/diamond.flac")


    def load_animation(self, path, frame_width, frame_height, num_frames, scale=None, trim=(0, 0, 0, 0)):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            # Trim the frame if needed.
            if trim != (0, 0, 0, 0):
                frame = frame.subsurface(pygame.Rect(trim[0], trim[1], frame_width - trim[2], frame_height - trim[3]))
            # Scale the frame if a scale is provided.
            if scale is not None:
                frame = pygame.transform.scale(frame, scale)
            frames.append(frame)
        return frames

    def update_animation(self):

        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            if self.state == "idle":
                # Loop the idle animation.
                self.frame_index = (self.frame_index + 1) % len(self.animations["idle"])
            elif self.state == "disappear":
                # Play disappearing animation once.
                if self.frame_index < len(self.animations["disappear"]) - 1:
                    self.frame_index += 1
                else:
                    self.kill()  # Remove the sprite when the animation completes.
            self.image = self.animations[self.state][self.frame_index]

    def update(self):
        self.update_animation()

    def collect(self):
        import settings
        if self.state != "disappear":
            self.state = "disappear"
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()
            self.sound.set_volume(settings.EFFECTS_VOLUME / 10.0)
            self.sound.play()


class Heart(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        heart_target_width = TILE_SIZE // 2
        heart_target_height = int(heart_target_width * 13 / 16)

        self.animations = {
            "idle": self.load_animation("assets/images/collectables/heart_idle.png", 18, 14, 8,
                                          scale=(heart_target_width, heart_target_height)),
            "disappear": self.load_animation("assets/images/collectables/heart_disappear.png", 12, 13, 2,
                                             scale=(heart_target_width, heart_target_height))
        }
        self.state = "idle"
        self.frame_index = 0
        self.frame_duration = 100
        self.last_update = pygame.time.get_ticks()

        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))

        self.sound = pygame.mixer.Sound("assets/sounds/other/health.flac")


    def load_animation(self, path, frame_width, frame_height, num_frames, scale=None, trim=(0, 0, 0, 0)):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            # Trim the frame if needed
            if trim != (0, 0, 0, 0):
                frame = frame.subsurface(pygame.Rect(trim[0], trim[1], frame_width - trim[2], frame_height - trim[3]))
            # Scale the frame if a scale is provided
            if scale is not None:
                frame = pygame.transform.scale(frame, scale)
            frames.append(frame)
        return frames

    def update_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            if self.state == "idle":
                self.frame_index = (self.frame_index + 1) % len(self.animations["idle"])
            elif self.state == "disappear":
                if self.frame_index < len(self.animations["disappear"]) - 1:
                    self.frame_index += 1
                else:
                    self.kill()
            self.image = self.animations[self.state][self.frame_index]

    def update(self):
        self.update_animation()

    def collect(self):
        import settings
        if self.state != "disappear":
            self.state = "disappear"
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()
            # Play the health collect sound
            self.sound.set_volume(settings.EFFECTS_VOLUME / 10.0)
            self.sound.play()
