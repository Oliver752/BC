import pygame
from settings import TILE_SIZE

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
        """
        Trigger the collection of the diamond.
        Switches the animation state to 'disappear' and resets the frame index.
        """
        if self.state != "disappear":
            self.state = "disappear"
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()
