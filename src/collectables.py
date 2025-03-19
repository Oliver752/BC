import pygame
from settings import TILE_SIZE, EFFECTS_VOLUME  # Import EFFECTS_VOLUME for volume settings

class Collectable(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Calculate target size for diamond to be half the tile size (maintaining aspect ratio)
        target_width = TILE_SIZE // 2
        target_height = int(target_width * 12 / 14)  # original diamond frame is 18x14 pixels

        # Load diamond animations similar to the player animations
        self.animations = {
            "idle": self.load_animation("assets/images/collectables/diamond_idle.png", 12, 10, 10, scale=(target_width, target_height)),
            "disappear": self.load_animation("assets/images/collectables/diamond_disappear.png", 12, 10, 2, scale=(target_width, target_height))
        }

        self.state = "idle"  # initial animation state
        self.frame_index = 0
        self.frame_duration = 100  # Duration per frame in milliseconds (adjust as needed)
        self.last_update = pygame.time.get_ticks()

        # Set the initial image and its rectangle (centered on the tile)
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))

        # --- Sound for diamond collection ---
        self.sound = pygame.mixer.Sound("assets/sounds/other/diamond.flac")


    def load_animation(self, path, frame_width, frame_height, num_frames, scale=None, trim=(0, 0, 0, 0)):
        """
        Load a spritesheet and slice it into frames.
        Parameters:
            path: The file path of the spritesheet.
            frame_width: The width of a single frame.
            frame_height: The height of a single frame.
            num_frames: The number of frames in the animation.
            scale: Optional tuple (width, height) to scale each frame.
            trim: Optional tuple (left, top, right, bottom) to trim the frame.
        Returns:
            A list of frames as pygame.Surface objects.
        """
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for i in range(num_frames):
            # Extract the frame from the spritesheet.
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
        """
        Update the animation based on the current state of the diamond.
        For the idle state, the animation loops continuously.
        For the disappear state, the animation plays once and then removes the sprite.
        """
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
        """Update the diamond's animation."""
        self.update_animation()

    def collect(self):
        import settings

        """
        Trigger the collection of the diamond.
        Switches the animation state to 'disappear' and resets the frame index.
        """
        if self.state != "disappear":
            self.state = "disappear"
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()
            # Play the diamond collect sound
            self.sound.set_volume(settings.EFFECTS_VOLUME / 10.0)
            self.sound.play()


class Heart(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Scale heart to be half the tile size; maintain aspect ratio (original frame: 12x13)
        heart_target_width = TILE_SIZE // 2
        heart_target_height = int(heart_target_width * 13 / 16)  # adjusted for 12x13 frames

        # Load heart animations using the provided spritesheets
        self.animations = {
            "idle": self.load_animation("assets/images/collectables/heart_idle.png", 18, 14, 8,
                                          scale=(heart_target_width, heart_target_height)),
            "disappear": self.load_animation("assets/images/collectables/heart_disappear.png", 12, 13, 2,
                                             scale=(heart_target_width, heart_target_height))
        }
        self.state = "idle"  # Initial state
        self.frame_index = 0
        self.frame_duration = 100  # Duration per frame in milliseconds
        self.last_update = pygame.time.get_ticks()

        # Set the initial image and rect centered in the tile
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))

        # --- Sound for heart (health) collection ---
        self.sound = pygame.mixer.Sound("assets/sounds/other/health.flac")


    def load_animation(self, path, frame_width, frame_height, num_frames, scale=None, trim=(0, 0, 0, 0)):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for i in range(num_frames):
            # Extract the frame (using the correct dimensions)
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
        """
        Update the heart's animation.
        Loops the idle animation; for disappear, plays once and then kills the sprite.
        """
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            if self.state == "idle":
                self.frame_index = (self.frame_index + 1) % len(self.animations["idle"])
            elif self.state == "disappear":
                if self.frame_index < len(self.animations["disappear"]) - 1:
                    self.frame_index += 1
                else:
                    self.kill()  # Remove the sprite when animation is done
            self.image = self.animations[self.state][self.frame_index]

    def update(self):
        """Update the heart collectible (animation only)."""
        self.update_animation()

    def collect(self):
        import settings

        """
        Trigger the collection of the heart.
        Switches to the disappearing animation.
        """
        if self.state != "disappear":
            self.state = "disappear"
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()
            # Play the health collect sound
            self.sound.set_volume(settings.EFFECTS_VOLUME / 10.0)
            self.sound.play()
