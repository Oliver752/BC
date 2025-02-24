import pygame
from settings import PLAYER_SPEED, PLAYER_JUMP, GRAVITY, TILE_SIZE
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Player animations (using the same cropping system)
        self.animations = {
            "idle_left": self.load_animation("assets/images/player/idle_left_spritesheet.png", 312, 232, 11),
            "idle_right": self.load_animation("assets/images/player/idle_right_spritesheet.png", 312, 232, 11),
            "run_left": self.load_animation("assets/images/player/run_left_spritesheet.png", 312, 232, 8),
            "run_right": self.load_animation("assets/images/player/run_right_spritesheet.png", 312, 232, 8),
            "jump_left": self.load_animation("assets/images/player/jump_left_spritesheet.png", 312, 232, 1),
            "jump_right": self.load_animation("assets/images/player/jump_right_spritesheet.png", 312, 232, 1),
            "fall_left": self.load_animation("assets/images/player/fall_left_spritesheet.png", 312, 232, 1),
            "fall_right": self.load_animation("assets/images/player/fall_right_spritesheet.png", 312, 232, 1),
            "ground_left": self.load_animation("assets/images/player/ground_left_spritesheet.png", 312, 232, 1),
            "ground_right": self.load_animation("assets/images/player/ground_right_spritesheet.png", 312, 232, 1),
        }

        self.current_animation = "idle_right"
        self.frame_index = 0
        self.image = self.animations[self.current_animation][self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.hitbox = pygame.Rect(
            self.rect.x + 110,  # Offset left
            self.rect.y + 56,   # Offset top
            self.rect.width - 220,  # Reduce width (110px from both sides)
            self.rect.height - 112  # Reduce height (56px from both top & bottom)
        )

        # Movement properties
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

        # Jumping properties
        self.can_double_jump = True
        self.jump_pressed = False  # Track if jump key is pressed

        # Direction tracking
        self.last_direction = "right"  # Default direction

        # Animation timing
        self.animation_speed = 0.1  # Controls frame rate
        self.last_update = pygame.time.get_ticks()

        # New flag to handle landing animation (plays for 1 frame)
        self.just_landed = False

    def update_hitbox(self):
        """Ensure the hitbox follows the player correctly."""
        self.hitbox.topleft = (self.rect.x + 110, self.rect.y + 56)

    def load_animation(self, path, frame_width, frame_height, num_frames, trim=(0, 0, 0, 0)):
        # Load a spritesheet and slice it into frames
        sheet = pygame.image.load(path).convert_alpha()
        trimmed_frames = []
        for i in range(num_frames):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            # Trim the frame if needed
            trimmed_frame = frame.subsurface(
                pygame.Rect(trim[0], trim[1], frame_width - trim[2], frame_height - trim[3])
            )
            trimmed_frames.append(trimmed_frame)
        return trimmed_frames

    def set_animation(self, animation):
        if self.current_animation != animation:
            self.current_animation = animation
            self.frame_index = 0

    def update_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 100:  # Adjust frame duration here
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_animation])
            self.image = self.animations[self.current_animation][self.frame_index]

    def move_and_collide(self, dx, dy, blocks):
        # Horizontal movement
        self.hitbox.x += dx
        for block in blocks:
            if self.hitbox.colliderect(block.rect):  # Check collision horizontally
                if dx > 0:  # Moving right
                    self.hitbox.right = block.rect.left
                if dx < 0:  # Moving left
                    self.hitbox.left = block.rect.right

        # Update player rect's x-position based on hitbox
        self.rect.x = self.hitbox.x - 110

        # Vertical movement
        # Store previous ground state to detect a landing event
        was_on_ground = self.on_ground
        # Assume air until collision tells otherwise
        self.on_ground = False
        self.hitbox.y += dy
        for block in blocks:
            if self.hitbox.colliderect(block.rect):  # Check collision vertically
                if dy > 0:  # Falling
                    self.hitbox.bottom = block.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.can_double_jump = True  # Reset double jump when grounded
                    # If the player was not grounded before, they just landed.
                    if not was_on_ground:
                        self.just_landed = True
                if dy < 0:  # Jumping upward
                    self.hitbox.top = block.rect.bottom
                    self.vel_y = 0

        # Update player rect's y-position based on hitbox
        self.rect.y = self.hitbox.y - 56

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0

        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
            self.last_direction = "left"
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
            self.last_direction = "right"

        # Handle jumping
        if keys[pygame.K_SPACE]:
            if not self.jump_pressed:  # Trigger jump only on key press, not hold
                if self.on_ground:  # Jump when grounded
                    self.vel_y = -PLAYER_JUMP
                    self.on_ground = False
                    self.can_double_jump = True  # Allow a double jump after leaving the ground
                elif self.can_double_jump:  # Allow double jump
                    self.vel_y = -PLAYER_JUMP
                    self.can_double_jump = False  # Disable further jumps until grounded
                self.jump_pressed = True  # Mark jump as pressed
        else:
            self.jump_pressed = False  # Reset jump press when key is released

    def apply_gravity(self):
        self.vel_y += GRAVITY
        if self.vel_y > 10:  # Cap falling speed
            self.vel_y = 10

    def update(self, blocks):
        # Handle movement and physics first
        self.handle_input()
        self.apply_gravity()
        self.move_and_collide(self.vel_x, self.vel_y, blocks)

        # Determine which animation to display based on current state.
        # Landing animation takes precedence (and plays for 1 frame).
        if self.just_landed:
            if self.last_direction == "right":
                self.set_animation("ground_right")
            else:
                self.set_animation("ground_left")
            # Reset after displaying landing frame.
            self.just_landed = False
        # If airborne, check if the player is moving upward (jumping) or downward (falling).
        elif not self.on_ground:
            if self.vel_y < 0:  # Ascending (jumping)
                if self.last_direction == "right":
                    self.set_animation("jump_right")
                else:
                    self.set_animation("jump_left")
            else:  # Descending (falling)
                if self.last_direction == "right":
                    self.set_animation("fall_right")
                else:
                    self.set_animation("fall_left")
        # If on the ground and not just landed, use horizontal movement animations.
        else:
            if self.vel_x > 0:
                self.set_animation("run_right")
            elif self.vel_x < 0:
                self.set_animation("run_left")
            else:
                if self.last_direction == "right":
                    self.set_animation("idle_right")
                else:
                    self.set_animation("idle_left")

        # Update the animation frame based on the current animation.
        self.update_animation()
        # Keep hitbox in sync with rect
        self.update_hitbox()
