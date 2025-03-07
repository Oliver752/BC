import pygame
import random
from settings import TILE_SIZE, SCREEN_WIDTH

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.animations = self.load_animation("assets/images/enemies/Enemy1/bomb_spritesheet.png", 19, 21, 4,scale_factor=5)
        self.explosion_anim = self.load_animation("assets/images/enemies/Enemy1/boom_spritesheet.png", 52, 56, 6,scale_factor=5)
        self.image = self.animations[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = 8 * direction  #  Increased bomb speed (was 5)

        self.vel_y = -15  # Initial upward motion
        self.gravity = 0.5
        self.exploding = False
        self.explosion_time = 0
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.spawn_time = pygame.time.get_ticks()
        self.bounced = False
    def load_animation(self, path, frame_width, frame_height, num_frames, scale_factor=2):
        """Load a spritesheet, extract frames, and scale them."""
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            #  Scale the bomb image (default scale_factor=2 doubles the size)
            scaled_frame = pygame.transform.scale(frame, (frame_width * scale_factor, frame_height * scale_factor))
            frames.append(scaled_frame)
        return frames

    def update(self, blocks, player):
        """Handle bomb physics: bounce off walls and bounce once on the ground, and prevent instant explosion."""
        now = pygame.time.get_ticks()

        if self.exploding:
            if now - self.explosion_time > 100:
                self.explosion_time = now
                self.frame_index += 1
                if self.frame_index >= len(self.explosion_anim):
                    self.kill()  # Remove bomb after explosion
                else:
                    self.image = self.explosion_anim[self.frame_index]
            return

        # Bombs explode 2.5 seconds after being thrown
        if now - self.spawn_time > 2500:
            self.start_explosion()
            return

        # Apply gravity
        self.vel_y += self.gravity

        # ---- Horizontal Movement & Collision ----
        self.rect.x += self.vel_x
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_x > 0:  # Moving right; hit left side of block
                    self.rect.right = block.rect.left
                elif self.vel_x < 0:  # Moving left; hit right side of block
                    self.rect.left = block.rect.right
                # Bounce horizontally by reversing and reducing speed slightly
                self.vel_x = -self.vel_x * 0.7

        # ---- Vertical Movement & Collision ----
        self.rect.y += self.vel_y
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_y > 0:  # Falling and colliding with the ground
                    self.rect.bottom = block.rect.top  # Align with block surface

                    # Allow one bounce on the ground
                    if not hasattr(self, "bounced_ground"):
                        self.vel_y = -5  # Small bounce upward
                        self.vel_x *= 0.7  # Reduce horizontal movement slightly
                        self.bounced_ground = True  # Flag so we only bounce once
                    else:
                        self.vel_y = 0  # Stop vertical movement after bounce
                        self.vel_x *= 0.8  # Gradually come to a stop
                        self.explode_timer = now  # Start countdown to explosion
                    return

                elif self.vel_y < 0:  # Hitting the ceiling
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0

    def start_explosion(self):
        """Triggers bomb explosion without incorrect offset on the first frame."""
        self.exploding = True
        self.frame_index = 0
        self.explosion_time = pygame.time.get_ticks()

        # Save the original center so the hitbox stays in the same place
        original_center = self.rect.center

        #  Directly assign the first explosion frame **without manually offsetting it**
        self.image = self.explosion_anim[self.frame_index]
        self.rect = self.image.get_rect(center=original_center)  #  Reset rect properly to center the image

        #  Set up the explosion hitbox (increase size if needed)
        explosion_radius = 100  # Adjust size if necessary
        self.explosion_rect = pygame.Rect(0, 0, explosion_radius * 2, explosion_radius * 2)
        self.explosion_rect.center = original_center  #  Ensure hitbox remains correctly positioned


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Load animations
        self.animations = {
            "idle_left": self.load_animation("assets/images/enemies/Enemy1/idle_spritesheet.png", 156, 156, 10),
            "run_left": self.load_animation("assets/images/enemies/Enemy1/run_spritesheet.png", 156, 156, 6),
            "throw_left": self.load_animation("assets/images/enemies/Enemy1/throw_spritesheet.png", 156, 156, 5),
            "pick_left": self.load_animation("assets/images/enemies/Enemy1/pick_bomb_spritesheet.png", 156, 156, 4),
            "hit_left": self.load_animation("assets/images/enemies/Enemy1/hit_spritesheet.png", 204, 168, 2),
            "dead_left": self.load_animation("assets/images/enemies/Enemy1/dead_spritesheet.png", 204, 168, 13),
        }

        # Flip animations for right side
        self.animations["idle_right"] = self.flip_animation("idle_left")
        self.animations["run_right"] = self.flip_animation("run_left")
        self.animations["throw_right"] = self.flip_animation("throw_left")
        self.animations["pick_right"] = self.flip_animation("pick_left")
        self.animations["hit_right"] = self.flip_animation("hit_left")
        self.animations["dead_right"] = self.flip_animation("dead_left")

        #  Set correct image size
        self.image = self.animations["idle_left"][0]
        self.rect = self.image.get_rect(topleft=(x, y - 20))  #  Adjust starting position slightly higher
        #  Adjust the hitbox to match the actual character size
        self.hitbox = pygame.Rect(self.rect.x + 15, self.rect.y + 15, 110, 110)  #  Shrinks the hitbox properly

        self.speed = 2
        self.direction = 1
        self.idle_timer = random.randint(1000, 3000)
        self.throw_cooldown = 3500
        self.last_throw_time = 0
        self.state = "patrol"
        self.health = 2

        # Timers for damage handling
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 500  # 0.5 seconds

        # Death state
        self.dying = False
        self.death_timer = 0

        self.frame_index = 0
        self.current_animation = "idle_left"  #  Set default animation
        self.last_update = pygame.time.get_ticks()



    def load_animation(self, path, frame_width, frame_height, num_frames):
        """Load a spritesheet and extract frames safely."""
        sheet = pygame.image.load(path).convert_alpha()
        sheet_width, _ = sheet.get_size()

        #  **Check if spritesheet width is large enough**
        max_frames = sheet_width // frame_width  # Calculate how many full frames exist
        num_frames = min(num_frames, max_frames)  # Avoid out-of-bounds access

        if num_frames == 0:
            raise ValueError(f"Error loading animation {path}: Not enough frames in the spritesheet.")

        return [sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)) for i in range(num_frames)]

    def flip_animation(self, key):
        return [pygame.transform.flip(frame, True, False) for frame in self.animations[key]]

    def set_animation(self, animation):
        """Change animation if different from current."""
        if self.current_animation != animation:
            self.current_animation = animation
            self.frame_index = 0

    def update_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 100:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_animation])
            self.image = self.animations[self.current_animation][self.frame_index]



    def patrol(self, blocks):
        """Moves left and right, stopping if colliding with a block."""
        original_x = self.hitbox.x  #  Store original position
        self.hitbox.x += self.direction * self.speed  #  Move first

        #  Check if colliding after movement
        for block in blocks:
            if self.hitbox.colliderect(block.rect):
                self.hitbox.x = original_x  #  Reset to previous position
                self.direction *= -1  #  Turn around
                return

        #  Apply movement to the main enemy rect after confirming no collision
        self.rect.x = self.hitbox.x

        #  Stop at ledges
        if self.check_fall(blocks):
            self.direction *= -1

    def check_fall(self, blocks):
        """Detect if the enemy is about to walk off a 1-block ledge and stop."""
        next_x = self.rect.x + (self.direction * TILE_SIZE)  # Move in direction of travel
        below_rect = pygame.Rect(next_x, self.rect.bottom, self.rect.width, 1)  #  Check just 1 pixel below

        #  If there is NO block right below, turn around
        for block in blocks:
            if block.rect.colliderect(below_rect):  #  Found ground directly below
                return False  # No fall risk

        return True  #  No ground → turn around

    def throw_bomb(self, player, bombs):
        """Throws a bomb in the direction of the player and switches to pick animation."""
        now = pygame.time.get_ticks()

        if now - self.last_throw_time > self.throw_cooldown:
            self.last_throw_time = now

            # Ensure enemy faces the player before throwing
            if player.rect.centerx > self.rect.centerx:
                self.direction = 1
                self.set_animation("throw_right")
            else:
                self.direction = -1
                self.set_animation("throw_left")

            # Throw bomb
            bomb_x = self.rect.centerx + (self.direction * 30)
            bomb_y = self.rect.centery - 10
            bomb = Bomb(bomb_x, bomb_y, self.direction)
            bombs.add(bomb)
            #  After throwing, switch to "pick"
            self.state = "pick"

    def update(self, player, blocks, bombs):
        """Update enemy state while ensuring hit and death animations play properly."""
        now = pygame.time.get_ticks()

        #  If dying, play death animation fully before removing
        if self.dying:
            if self.frame_index >= len(self.animations["dead_left"]) - 1:
                self.kill()  # Remove enemy after animation completes
                return
            self.update_animation()
            return  #  Prevent further logic while dying

        #  If hit, play hit animation before returning to normal
        if self.invulnerable:
            if now - self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable = False  #  End invulnerability
                self.set_animation("idle_right" if self.direction == 1 else "idle_left")
            else:
                self.update_animation()
                return  #  Don't update movement until hit animation finishes

        #  Continue enemy logic if not in hit or death state
        player_distance = abs(self.rect.centerx - player.rect.centerx)

        if self.state == "idle":
            if now - self.last_throw_time > self.throw_cooldown:
                self.state = "throw"
            elif player_distance > 600:
                self.state = "patrol"

        elif self.state == "patrol":
            if player_distance < 600:
                self.state = "throw"
            else:
                self.patrol(blocks)

        elif self.state == "throw":
            self.throw_bomb(player, bombs)
            if self.frame_index >= len(self.animations[self.current_animation]) - 1:
                self.state = "pick"

        elif self.state == "pick":
            if self.frame_index >= len(self.animations[self.current_animation]) - 1:
                self.state = "idle"

        #  Ensure movement animations are properly set
        if self.state == "patrol":
            self.set_animation("run_left" if self.direction == -1 else "run_right")
        elif self.state == "idle":
            self.set_animation("idle_left" if self.direction == -1 else "idle_right")
        elif self.state == "throw":
            self.set_animation("throw_left" if self.direction == -1 else "throw_right")
        elif self.state == "pick":
            self.set_animation("pick_left" if self.direction == -1 else "pick_right")

        self.update_animation()

    def take_damage(self):
        """Reduce health and trigger hit animation, with invulnerability."""
        if self.invulnerable or self.dying:
            return  # Ignore damage if the enemy is already invulnerable or dying

        self.health -= 1

        if self.health <= 0:
            self.dying = True
            self.death_timer = pygame.time.get_ticks()
            self.set_animation("dead_right" if self.direction == 1 else "dead_left")
        else:
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            self.set_animation("hit_right" if self.direction == 1 else "hit_left")
