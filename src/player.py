import pygame
from settings import PLAYER_SPEED, PLAYER_JUMP, GRAVITY, TILE_SIZE


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Player animations (keeping everything!)
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
            "attack_left": self.load_animation("assets/images/player/attack_left_spritesheet.png", 312, 232, 3),
            "attack_right": self.load_animation("assets/images/player/attack_right_spritesheet.png", 312, 232, 3),
        }

        # Player health
        self.health = 2
        self.max_health = 3

        # State tracking
        self.current_animation = "idle_right"
        self.frame_index = 0
        self.image = self.animations[self.current_animation][self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Hitbox adjustment
        self.hitbox = pygame.Rect(
            self.rect.x + 110,
            self.rect.y + 56,
            self.rect.width - 220,
            self.rect.height - 112
        )

        # Movement & physics
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.can_double_jump = True
        self.jump_pressed = False
        self.last_direction = "right"

        # Attack properties
        self.attacking = False
        self.attack_duration = 500  # Attack lasts 300ms
        self.attack_start_time = 0

        # Animation timing
        self.last_update = pygame.time.get_ticks()

    def update_hitbox(self):
        """Ensure the hitbox follows the player correctly."""
        self.hitbox.topleft = (self.rect.x + 110, self.rect.y + 56)

    def load_animation(self, path, frame_width, frame_height, num_frames):
        """Load spritesheet and extract frames."""
        sheet = pygame.image.load(path).convert_alpha()
        return [sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)) for i in range(num_frames)]

    def set_animation(self, animation):
        """Change animation if different from current."""
        if self.current_animation != animation:
            self.current_animation = animation
            self.frame_index = 0

    def attack(self):
        """Triggers attack animation but allows movement."""
        if not self.attacking:  # Prevent spamming attack
            self.attacking = True
            self.attack_start_time = pygame.time.get_ticks()

            # Set attack animation based on direction
            if self.last_direction == "right":
                self.set_animation("attack_right")
            else:
                self.set_animation("attack_left")

            self.frame_index = 0  # Ensure first frame starts
            self.image = self.animations[self.current_animation][self.frame_index]  # Force first frame

    def update_animation(self):
        """Update player's animation without interrupting attack."""
        now = pygame.time.get_ticks()

        # Ensure attack animation plays fully before switching back
        if self.attacking:
            if now - self.attack_start_time > self.attack_duration:
                self.attacking = False  # End attack after duration

        if now - self.last_update > 100:  # Adjust frame speed
            self.last_update = now

            # Only advance frames if attacking
            if self.attacking:
                if self.frame_index < len(self.animations[self.current_animation]) - 1:
                    self.frame_index += 1  # Advance attack animation
                else:
                    self.attacking = False  # Attack animation finished
                    self.set_animation("idle_right" if self.last_direction == "right" else "idle_left")
            else:
                # Regular animations (only update if not attacking)
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_animation])

            self.image = self.animations[self.current_animation][self.frame_index]

    def handle_input(self):
        """Handles movement and attack input."""
        keys = pygame.key.get_pressed()

        if not self.attacking:  # Prevent movement during attack
            self.vel_x = 0

            if keys[pygame.K_LEFT]:
                self.vel_x = -PLAYER_SPEED
                self.last_direction = "left"
            if keys[pygame.K_RIGHT]:
                self.vel_x = PLAYER_SPEED
                self.last_direction = "right"

            # Handle jumping
            if keys[pygame.K_UP]:  # Jump with UP arrow
                if not self.jump_pressed:
                    if self.on_ground:
                        self.vel_y = -PLAYER_JUMP
                        self.on_ground = False
                        self.can_double_jump = True
                    elif self.can_double_jump:
                        self.vel_y = -PLAYER_JUMP
                        self.can_double_jump = False
                    self.jump_pressed = True
            else:
                self.jump_pressed = False  # Reset jump press

        # Attack with SPACE
        if keys[pygame.K_SPACE]:
            self.attack()

    def apply_gravity(self):
        """Apply gravity to player."""
        self.vel_y += GRAVITY
        if self.vel_y > 10:  # Cap falling speed
            self.vel_y = 10

    def move_and_collide(self, dx, dy, blocks):
        """Handle movement and collisions."""
        self.hitbox.x += dx
        for block in blocks:
            if self.hitbox.colliderect(block.rect):  # Horizontal collision
                if dx > 0:
                    self.hitbox.right = block.rect.left
                if dx < 0:
                    self.hitbox.left = block.rect.right
        self.rect.x = self.hitbox.x - 110

        was_on_ground = self.on_ground
        self.on_ground = False
        self.hitbox.y += dy
        for block in blocks:
            if self.hitbox.colliderect(block.rect):  # Vertical collision
                if dy > 0:
                    self.hitbox.bottom = block.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.can_double_jump = True
                    if not was_on_ground:
                        self.just_landed = True
                if dy < 0:
                    self.hitbox.top = block.rect.bottom
                    self.vel_y = 0
        self.rect.y = self.hitbox.y - 56

    def update(self, blocks, bombs):
        """Update player state, movement, animations, and handle bomb collisions."""
        self.handle_input()
        self.apply_gravity()
        self.move_and_collide(self.vel_x, self.vel_y, blocks)

        # Check for bomb collisions
        for bomb in bombs:
            if bomb.exploding and self.hitbox.colliderect(bomb.rect):
                self.health -= 1
                bomb.kill()  # Remove bomb after damage is applied

        # Do not override attack animation with movement animations
        # Do not override attack animation with movement animations
        if not self.attacking:
            if self.on_ground:
                if self.vel_x > 0:
                    self.set_animation("run_right")
                elif self.vel_x < 0:
                    self.set_animation("run_left")
                else:
                    self.set_animation("idle_right" if self.last_direction == "right" else "idle_left")
            else:
                # Check if the player is moving upward (jumping) or downward (falling)
                if self.vel_y < 0:
                    self.set_animation("jump_right" if self.last_direction == "right" else "jump_left")
                else:
                    self.set_animation("fall_right" if self.last_direction == "right" else "fall_left")

        self.update_animation()
        self.update_hitbox()
0

