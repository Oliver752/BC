import pygame
from settings import TILE_SIZE, EFFECTS_VOLUME

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y, required_gems):
        super().__init__()
        # Load the closed door image and scale it (using TILE_SIZE for consistency)
        self.closed_image = pygame.image.load("assets/images/blocks/door.png").convert_alpha()
        self.closed_image = pygame.transform.scale(self.closed_image, (TILE_SIZE, TILE_SIZE))

        # Load door opening animation (door_open.png has 5 frames, each 138x168px)
        door_open_sheet = pygame.image.load("assets/images/blocks/door_open.png").convert_alpha()
        self.open_frames = []
        frame_width = 128
        frame_height = 128
        for i in range(5):
            frame = door_open_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            self.open_frames.append(frame)

        # Load UI assets for the text bubble and arrow
        self.button_img = pygame.image.load("assets/images/btn/button.png").convert_alpha()
        self.button_img = pygame.transform.scale(self.button_img, (100, 50))  # adjust size as needed
        self.arrow_img = pygame.image.load("assets/images/btn/arrow_down.png").convert_alpha()
        self.arrow_img = pygame.transform.scale(self.arrow_img, (50, 50))

        # -------------------------------
        # NEW: Load door opening sound
        self.sound_open = pygame.mixer.Sound("assets/sounds/other/door.wav")
        # -------------------------------

        # Initial state: "closed" then "opening" and finally "open"
        self.state = "closed"
        self.frame_index = 0
        self.animation_delay = 100  # milliseconds per frame for door opening
        self.last_update = pygame.time.get_ticks()
        self.required_gems = required_gems
        self.rect = self.closed_image.get_rect(topleft=(x, y))

    def update(self, current_gems, player, keys):
        import settings
        # When gems are collected, begin opening
        if self.state == "closed" and current_gems >= self.required_gems:
            self.state = "opening"
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()
            # Play door opening sound once
            self.sound_open.set_volume(settings.EFFECTS_VOLUME / 10.0/2)
            self.sound_open.play()

        # Advance door opening animation
        if self.state == "opening":
            now = pygame.time.get_ticks()
            if now - self.last_update >= self.animation_delay:
                self.last_update = now
                self.frame_index += 1
                if self.frame_index >= len(self.open_frames):
                    self.frame_index = len(self.open_frames) - 1
                    self.state = "open"

        # When open, if player overlaps and the down arrow is pressed, trigger door entry
        if self.state == "open":
            if self.rect.colliderect(player.rect) and keys[pygame.K_DOWN]:
                if not player.door_entry:
                    player.start_door_entry()

    def get_current_image(self):
        if self.state == "closed":
            return self.closed_image
        else:
            return self.open_frames[self.frame_index]

    def draw_image(self, screen, camera):
        # Draw just the door image behind other sprites.
        pos = camera.apply(self)
        door_img = self.get_current_image()
        screen.blit(door_img, pos)

    def draw_ui(self, screen, font, current_gems, camera):
        pos = camera.apply(self)
        if self.state != "open":
            # For the gem counter, keep the bubble centered above the door.
            bubble_rect = self.button_img.get_rect(midbottom=(pos.centerx, pos.top - 10))
            screen.blit(self.button_img, bubble_rect)
            text = f"{current_gems}/{self.required_gems}"
            text_surf = font.render(text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=bubble_rect.center)
            screen.blit(text_surf, text_rect)
            diamond_icon = pygame.image.load("assets/images/hud/diamond.png").convert_alpha()
            diamond_icon = pygame.transform.scale(diamond_icon, (32, 32))
            diamond_rect = diamond_icon.get_rect(right=text_rect.left - 5, centery=text_rect.centery)
            screen.blit(diamond_icon, diamond_rect)
        else:
            # When open, shift the arrow as needed.
            bubble_rect = self.button_img.get_rect(midbottom=(pos.centerx + 25, pos.top - 15))
            screen.blit(self.arrow_img, bubble_rect)
