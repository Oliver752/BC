import pygame
import random
import math
from settings import TILE_SIZE, SCREEN_WIDTH

# ---------------------------
# Bomb class (unchanged)
# ---------------------------
class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.animations = self.load_animation("assets/images/enemies/Enemy1/bomb_spritesheet.png", 19, 21, 4,
                                              scale_factor=5)
        self.explosion_anim = self.load_animation("assets/images/enemies/Enemy1/boom_spritesheet.png", 52, 56, 6,
                                                  scale_factor=5)
        self.image = self.animations[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = 8 * direction
        self.vel_y = -15
        self.gravity = 0.5
        self.exploding = False
        self.explosion_time = 0
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.spawn_time = pygame.time.get_ticks()
        self.bounced = False

    def load_animation(self, path, frame_width, frame_height, num_frames, scale_factor=2):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            scaled_frame = pygame.transform.scale(frame, (frame_width * scale_factor, frame_height * scale_factor))
            frames.append(scaled_frame)
        return frames

    def update(self, blocks, player):
        now = pygame.time.get_ticks()
        if self.exploding:
            if now - self.explosion_time > 100:
                self.explosion_time = now
                self.frame_index += 1
                if self.frame_index >= len(self.explosion_anim):
                    self.kill()
                else:
                    self.image = self.explosion_anim[self.frame_index]
            return

        if now - self.spawn_time > 2500:
            self.start_explosion()
            return

        self.vel_y += self.gravity
        self.rect.x += self.vel_x
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_x > 0:
                    self.rect.right = block.rect.left
                elif self.vel_x < 0:
                    self.rect.left = block.rect.right
                self.vel_x = -self.vel_x * 0.7

        self.rect.y += self.vel_y
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vel_y > 0:
                    self.rect.bottom = block.rect.top
                    if not hasattr(self, "bounced_ground"):
                        self.vel_y = -5
                        self.vel_x *= 0.7
                        self.bounced_ground = True
                    else:
                        self.vel_y = 0
                        self.vel_x *= 0.8
                        self.explode_timer = now
                    return
                elif self.vel_y < 0:
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0

    def start_explosion(self):
        self.exploding = True
        self.frame_index = 0
        self.explosion_time = pygame.time.get_ticks()
        original_center = self.rect.center
        self.image = self.explosion_anim[self.frame_index]
        self.rect = self.image.get_rect(center=original_center)
        explosion_radius = 100
        self.explosion_rect = pygame.Rect(0, 0, explosion_radius * 2, explosion_radius * 2)
        self.explosion_rect.center = original_center


# ---------------------------
# BaseEnemy class
# ---------------------------
class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.direction = 1
        self.health = 2
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 500
        self.dying = False
        self.death_timer = 0
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.animations = {}
        self.current_animation = ""
        self.image = None
        self.rect = None
        self.hitbox = None

    def load_animation(self, path, frame_width, frame_height, num_frames, scale_factor=1):
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        for i in range(num_frames):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            if scale_factor != 1:
                frame = pygame.transform.scale(
                    frame,
                    (int(frame_width * scale_factor), int(frame_height * scale_factor))
                )
            frames.append(frame)
        return frames

    def flip_animation(self, anim_key):
        return [pygame.transform.flip(frame, True, False) for frame in self.animations[anim_key]]

    def set_animation(self, animation):
        if self.current_animation != animation:
            self.current_animation = animation
            self.frame_index = 0

    def update_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 100:
            self.last_update = now
            if self.current_animation in self.animations:
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_animation])
                self.image = self.animations[self.current_animation][self.frame_index]

    def take_damage(self):
        if self.invulnerable or self.dying:
            return
        self.health -= 1
        if self.health <= 0:
            self.dying = True
            self.death_timer = pygame.time.get_ticks()
            if self.direction == 1:
                self.set_animation("dead_right")
            else:
                self.set_animation("dead_left")
        else:
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            if self.direction == 1:
                self.set_animation("hit_right")
            else:
                self.set_animation("hit_left")


# ---------------------------
# BomberPig class
# ---------------------------
class BomberPig(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.animations = {
            "idle_left": self.load_animation("assets/images/enemies/Enemy1/idle_spritesheet.png", 156, 156, 10),
            "run_left": self.load_animation("assets/images/enemies/Enemy1/run_spritesheet.png", 156, 156, 6),
            "throw_left": self.load_animation("assets/images/enemies/Enemy1/throw_spritesheet.png", 156, 156, 5),
            "pick_left": self.load_animation("assets/images/enemies/Enemy1/pick_bomb_spritesheet.png", 156, 156, 4),
            "hit_left": self.load_animation("assets/images/enemies/Enemy1/hit_spritesheet.png", 204, 168, 2),
            "dead_left": self.load_animation("assets/images/enemies/Enemy1/dead_spritesheet.png", 204, 168, 13),
        }
        self.animations["idle_right"] = self.flip_animation("idle_left")
        self.animations["run_right"] = self.flip_animation("run_left")
        self.animations["throw_right"] = self.flip_animation("throw_left")
        self.animations["pick_right"] = self.flip_animation("pick_left")
        self.animations["hit_right"] = self.flip_animation("hit_left")
        self.animations["dead_right"] = self.flip_animation("dead_left")

        self.image = self.animations["idle_left"][0]
        self.rect = self.image.get_rect(topleft=(x, y - 20))
        self.hitbox = pygame.Rect(self.rect.x + 15, self.rect.y + 15, 110, 110)

        self.speed = 2
        self.idle_timer = random.randint(1000, 3000)
        self.throw_cooldown = 3500
        self.last_throw_time = 0
        self.state = "patrol"

    def patrol(self, blocks):
        original_x = self.hitbox.x
        self.hitbox.x += self.direction * self.speed
        for block in blocks:
            if self.hitbox.colliderect(block.rect):
                self.hitbox.x = original_x
                self.direction *= -1
                return
        self.rect.x = self.hitbox.x
        if self.check_fall(blocks):
            self.direction *= -1

    def check_fall(self, blocks):
        next_x = self.rect.x + (self.direction * TILE_SIZE)
        below_rect = pygame.Rect(next_x, self.rect.bottom, self.rect.width, 1)
        for block in blocks:
            if block.rect.colliderect(below_rect):
                return False
        return True

    def throw_bomb(self, player, bombs):
        now = pygame.time.get_ticks()
        if now - self.last_throw_time > self.throw_cooldown:
            self.last_throw_time = now
            if player.rect.centerx > self.rect.centerx:
                self.direction = 1
                self.set_animation("throw_right")
            else:
                self.direction = -1
                self.set_animation("throw_left")
            bomb_x = self.rect.centerx + (self.direction * 30)
            bomb_y = self.rect.centery - 10
            bomb = Bomb(bomb_x, bomb_y, self.direction)
            bombs.add(bomb)
            self.state = "pick"

    def update(self, player, blocks, bombs):
        now = pygame.time.get_ticks()
        if self.dying:
            if self.frame_index >= len(self.animations["dead_left"]) - 1:
                self.kill()
                return
            self.update_animation()
            return
        if self.invulnerable:
            if now - self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable = False
                self.set_animation("idle_right" if self.direction == 1 else "idle_left")
            else:
                self.update_animation()
                return

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

        if self.state == "patrol":
            self.set_animation("run_left" if self.direction == -1 else "run_right")
        elif self.state == "idle":
            self.set_animation("idle_left" if self.direction == -1 else "idle_right")
        elif self.state == "throw":
            self.set_animation("throw_left" if self.direction == -1 else "throw_right")
        elif self.state == "pick":
            self.set_animation("pick_left" if self.direction == -1 else "pick_right")

        self.update_animation()


# ---------------------------
# Pig class
# ---------------------------
class Pig(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        # --- Load animations ---
        self.animations = {
            "idle_left":   self.load_animation("assets/images/enemies/Enemy2/idle_spritesheet.png", 136, 112, 11),
            "run_left":    self.load_animation("assets/images/enemies/Enemy2/run_spritesheet.png", 136, 112, 6),
            "jump_left":   self.load_animation("assets/images/enemies/Enemy2/jump_spritesheet.png", 136, 112, 1),
            "fall_left":   self.load_animation("assets/images/enemies/Enemy2/fall_spritesheet.png", 136, 112, 1),
            "ground_left": self.load_animation("assets/images/enemies/Enemy2/ground_spritesheet.png", 136, 112, 1),
            "attack_left": self.load_animation("assets/images/enemies/Enemy2/attack_spritesheet.png", 136, 112, 5),
            "hit_left":    self.load_animation("assets/images/enemies/Enemy2/hit_spritesheet.png", 136, 112, 2),
            "dead_left":   self.load_animation("assets/images/enemies/Enemy2/dead_spritesheet.png", 136, 112, 11),
        }
        # Flip for right side
        self.animations["idle_right"]   = self.flip_animation("idle_left")
        self.animations["run_right"]    = self.flip_animation("run_left")
        self.animations["jump_right"]   = self.flip_animation("jump_left")
        self.animations["fall_right"]   = self.flip_animation("fall_left")
        self.animations["ground_right"] = self.flip_animation("ground_left")
        self.animations["attack_right"] = self.flip_animation("attack_left")
        self.animations["hit_right"]    = self.flip_animation("hit_left")
        self.animations["dead_right"]   = self.flip_animation("dead_left")

        # --- Position & Hitbox ---
        self.image = self.animations["idle_left"][0]
        self.rect  = self.image.get_rect(topleft=(x, y - 20))
        self.hitbox= pygame.Rect(self.rect.x + 15, self.rect.y + 15, 100, 100)

        # Movement/Physics
        self.direction   = 1
        self.speed       = 2
        self.vel_y       = 0
        self.gravity     = 0.5
        self.jump_force  = 13
        self.jump_cooldown  = 1000
        self.last_jump_time  = 0

        # Attack
        self.chase_range      = 500
        self.attack_range     = 50
        self.attack_cooldown  = 2000
        self.attack_duration  = 800
        self.last_attack_time = 0
        self.damage_done      = False

        # States & Timers
        self.state          = "patrol"
        self.idle_timer     = 2000
        self.last_idle_time = pygame.time.get_ticks()

        # Landing
        self.landed_delay = 150
        self.landed_time  = 0

        # Flip threshold
        self.direction_threshold = 5

    # Removed draw_debug from Pig

    def move_and_collide(self, dx, dy, blocks):
        # Horizontal
        self.hitbox.x += dx
        for block in blocks:
            if self.hitbox.colliderect(block.rect):
                if dx > 0:
                    self.hitbox.right = block.rect.left
                elif dx < 0:
                    self.hitbox.left = block.rect.right
        self.rect.x = self.hitbox.x - 15

        # Vertical
        self.hitbox.y += dy
        for block in blocks:
            if self.hitbox.colliderect(block.rect):
                if dy > 0:
                    self.hitbox.bottom = block.rect.top
                    self.vel_y = 0
                else:
                    self.hitbox.top = block.rect.bottom
                    self.vel_y = 0
        self.rect.y = self.hitbox.y - 15

    def on_ground(self, blocks):
        test_rect = self.hitbox.copy()
        test_rect.y += 5
        return any(test_rect.colliderect(b.rect) for b in blocks)

    def check_ledge(self, blocks):
        foot_offset = 30
        foot_width  = 20
        foot_height = 5
        foot_rect = pygame.Rect(
            self.hitbox.centerx + (self.direction * foot_offset) - (foot_width // 2),
            self.hitbox.bottom,
            foot_width,
            foot_height
        )
        return not any(foot_rect.colliderect(b.rect) for b in blocks)

    def update(self, player, blocks):
        now = pygame.time.get_ticks()
        if self.dying:
            if self.frame_index >= len(self.animations["dead_left"]) - 1:
                self.kill()
                return
            self.update_animation()
            return
        if self.invulnerable:
            if now - self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable = False
                self.set_animation("idle_right" if self.direction == 1 else "idle_left")
            else:
                self.update_animation()
                return

        if self.state == "attack":
            self.handle_attack(player, now)
        else:
            self.handle_ai(player, now, blocks)

        self.vel_y += self.gravity
        if self.vel_y > 10:
            self.vel_y = 10
        self.move_and_collide(0, self.vel_y, blocks)

        self.set_proper_animation(blocks)
        self.update_animation()

    def handle_attack(self, player, now):
        if not self.damage_done and self.hitbox.colliderect(player.hitbox):
            player.take_damage(source="enemy", invuln_duration=500)
            self.damage_done = True
        if now - self.last_attack_time > self.attack_duration:
            self.state = "chase"

    def handle_ai(self, player, now, blocks):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        can_attack = (now - self.last_attack_time > self.attack_cooldown)

        if dist < self.attack_range and can_attack:
            self.state = "attack"
            self.last_attack_time = now
            self.damage_done = False
            if abs(dx) > self.direction_threshold:
                self.direction = 1 if dx > 0 else -1
        elif dist < self.chase_range:
            self.state = "chase"
            if abs(dx) > self.direction_threshold:
                self.direction = 1 if dx > 0 else -1
        else:
            if self.state not in ("patrol", "idle"):
                self.state = "patrol"
                self.last_idle_time = now
            if now - self.last_idle_time > self.idle_timer:
                self.state = "idle" if self.state == "patrol" else "patrol"
                self.last_idle_time = now

        if self.state == "patrol":
            self.handle_movement(blocks, allow_jump=False, check_ledge=True)
        elif self.state == "idle":
            pass
        elif self.state == "chase":
            self.handle_movement(blocks, allow_jump=True, check_ledge=False)

    def handle_movement(self, blocks, allow_jump, check_ledge):
        dx = self.direction * self.speed
        if check_ledge and self.check_ledge(blocks):
            dx = 0
            self.direction *= -1

        old_x = self.hitbox.x
        self.hitbox.x += dx
        blocked = any(self.hitbox.colliderect(b.rect) for b in blocks)
        if blocked:
            self.hitbox.x = old_x
            if allow_jump:
                now = pygame.time.get_ticks()
                if now - self.last_jump_time > self.jump_cooldown:
                    self.vel_y = -self.jump_force
                    self.last_jump_time = now
            else:
                self.direction *= -1
        self.rect.x = self.hitbox.x - 15

    def set_proper_animation(self, blocks):
        if self.state == "attack":
            self.set_animation("attack_left" if self.direction == -1 else "attack_right")
            return
        on_ground_now = self.on_ground(blocks)
        if not on_ground_now:
            if self.vel_y < 0:
                self.set_animation("jump_left" if self.direction == -1 else "jump_right")
            else:
                self.set_animation("fall_left" if self.direction == -1 else "fall_right")
        else:
            if "fall" in self.current_animation:
                self.set_animation("ground_left" if self.direction == -1 else "ground_right")
                return
            if self.state == "idle":
                self.set_animation("idle_left" if self.direction == -1 else "idle_right")
            elif self.state in ("patrol", "chase"):
                self.set_animation("run_left" if self.direction == -1 else "run_right")


# ---------------------------
# King class (new enemy)
# ---------------------------
class King(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        # Load animations for the King (frame size 190x140).
        self.animations = {
            "idle_left":   self.load_animation("assets/images/enemies/Enemy3/idle_spritesheet.png",   190, 140, 12),
            "run_left":    self.load_animation("assets/images/enemies/Enemy3/run_spritesheet.png",    190, 140, 6),
            "jump_left":   self.load_animation("assets/images/enemies/Enemy3/jump_spritesheet.png",   190, 140, 1),
            "fall_left":   self.load_animation("assets/images/enemies/Enemy3/fall_spritesheet.png",   190, 140, 1),
            "ground_left": self.load_animation("assets/images/enemies/Enemy3/ground_spritesheet.png", 190, 140, 1),
            "attack_left": self.load_animation("assets/images/enemies/Enemy3/attack_spritesheet.png", 190, 140, 5),
            "hit_left":    self.load_animation("assets/images/enemies/Enemy3/hit_spritesheet.png",    190, 140, 2),
            "dead_left":   self.load_animation("assets/images/enemies/Enemy3/dead_spritesheet.png",   190, 140, 11),
        }
        # Flip for right side
        self.animations["idle_right"]   = self.flip_animation("idle_left")
        self.animations["run_right"]    = self.flip_animation("run_left")
        self.animations["jump_right"]   = self.flip_animation("jump_left")
        self.animations["fall_right"]   = self.flip_animation("fall_left")
        self.animations["ground_right"] = self.flip_animation("ground_left")
        self.animations["attack_right"] = self.flip_animation("attack_left")
        self.animations["hit_right"]    = self.flip_animation("hit_left")
        self.animations["dead_right"]   = self.flip_animation("dead_left")

        # Position & Hitbox
        self.image = self.animations["idle_left"][0]
        self.rect  = self.image.get_rect(topleft=(x, y - 20))
        self.hitbox= pygame.Rect(self.rect.x + 15, self.rect.y + 15, 100, 120)

        # Draw debug for King
        self.debug       = True

        # Movement/Physics
        self.direction   = 1
        self.speed       = 2
        self.vel_y       = 0
        self.gravity     = 0.5
        self.jump_force  = 15
        self.jump_cooldown  = 1000
        self.last_jump_time  = 0

        # Attack
        self.health = 5
        self.chase_range      = 500
        self.attack_range     = 50
        self.attack_cooldown  = 2000
        self.attack_duration  = 800
        self.last_attack_time = 0
        self.damage_done      = False

        # States & Timers
        self.state          = "patrol"
        self.idle_timer     = 2000
        self.last_idle_time = pygame.time.get_ticks()

        # Landing
        self.landed_delay = 150
        self.landed_time  = 0

        # Flip threshold
        self.direction_threshold = 5

    def draw_debug(self, surface, camera):
        """Draw the King's hitbox in red, offset by the camera."""
        offset = camera.camera.topleft
        debug_rect = self.hitbox.copy()
        debug_rect.x += offset[0]
        debug_rect.y += offset[1]
        pygame.draw.rect(surface, (255, 0, 0), debug_rect, 2)

    def move_and_collide(self, dx, dy, blocks):
        self.hitbox.x += dx
        for block in blocks:
            if self.hitbox.colliderect(block.rect):
                if dx > 0:
                    self.hitbox.right = block.rect.left
                elif dx < 0:
                    self.hitbox.left = block.rect.right
        self.rect.x = self.hitbox.x - 15

        self.hitbox.y += dy
        for block in blocks:
            if self.hitbox.colliderect(block.rect):
                if dy > 0:
                    self.hitbox.bottom = block.rect.top
                    self.vel_y = 0
                else:
                    self.hitbox.top = block.rect.bottom
                    self.vel_y = 0
        self.rect.y = self.hitbox.y - 15

    def on_ground(self, blocks):
        test_rect = self.hitbox.copy()
        test_rect.y += 5
        return any(test_rect.colliderect(b.rect) for b in blocks)

    def check_ledge(self, blocks):
        foot_offset = 30
        foot_width  = 20
        foot_height = 5
        foot_rect = pygame.Rect(
            self.hitbox.centerx + (self.direction * foot_offset) - (foot_width // 2),
            self.hitbox.bottom,
            foot_width,
            foot_height
        )
        return not any(foot_rect.colliderect(b.rect) for b in blocks)

    def update(self, player, blocks):
        now = pygame.time.get_ticks()
        if self.dying:
            if self.frame_index >= len(self.animations["dead_left"]) - 1:
                self.kill()
                return
            self.update_animation()
            return
        if self.invulnerable:
            if now - self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable = False
                self.set_animation("idle_right" if self.direction == 1 else "idle_left")
            else:
                self.update_animation()
                return

        if self.state == "attack":
            self.handle_attack(player, now)
        else:
            self.handle_ai(player, now, blocks)

        self.vel_y += self.gravity
        if self.vel_y > 10:
            self.vel_y = 10
        self.move_and_collide(0, self.vel_y, blocks)

        self.set_proper_animation(blocks)
        self.update_animation()

    def handle_attack(self, player, now):
        if not self.damage_done and self.hitbox.colliderect(player.hitbox):
            player.take_damage(source="enemy", invuln_duration=500)
            self.damage_done = True
        if now - self.last_attack_time > self.attack_duration:
            self.state = "chase"

    def handle_ai(self, player, now, blocks):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        can_attack = (now - self.last_attack_time > self.attack_cooldown)

        if dist < self.attack_range and can_attack:
            self.state = "attack"
            self.last_attack_time = now
            self.damage_done = False
            if abs(dx) > self.direction_threshold:
                self.direction = 1 if dx > 0 else -1
        elif dist < self.chase_range:
            self.state = "chase"
            if abs(dx) > self.direction_threshold:
                self.direction = 1 if dx > 0 else -1
        else:
            if self.state not in ("patrol", "idle"):
                self.state = "patrol"
                self.last_idle_time = now
            if now - self.last_idle_time > self.idle_timer:
                self.state = "idle" if self.state == "patrol" else "patrol"
                self.last_idle_time = now

        if self.state == "patrol":
            self.handle_movement(blocks, allow_jump=False, check_ledge=True)
        elif self.state == "idle":
            pass
        elif self.state == "chase":
            self.handle_movement(blocks, allow_jump=True, check_ledge=False)

    def handle_movement(self, blocks, allow_jump, check_ledge):
        dx = self.direction * self.speed
        if check_ledge and self.check_ledge(blocks):
            dx = 0
            self.direction *= -1

        old_x = self.hitbox.x
        self.hitbox.x += dx
        blocked = any(self.hitbox.colliderect(b.rect) for b in blocks)
        if blocked:
            self.hitbox.x = old_x
            if allow_jump:
                now = pygame.time.get_ticks()
                if now - self.last_jump_time > self.jump_cooldown:
                    self.vel_y = -self.jump_force
                    self.last_jump_time = now
            else:
                self.direction *= -1
        self.rect.x = self.hitbox.x - 15

    def set_proper_animation(self, blocks):
        if self.state == "attack":
            self.set_animation("attack_left" if self.direction == -1 else "attack_right")
            return
        on_ground_now = self.on_ground(blocks)
        if not on_ground_now:
            if self.vel_y < 0:
                self.set_animation("jump_left" if self.direction == -1 else "jump_right")
            else:
                self.set_animation("fall_left" if self.direction == -1 else "fall_right")
        else:
            if "fall" in self.current_animation:
                self.set_animation("ground_left" if self.direction == -1 else "ground_right")
                return
            if self.state == "idle":
                self.set_animation("idle_left" if self.direction == -1 else "idle_right")
            elif self.state in ("patrol", "chase"):
                self.set_animation("run_left" if self.direction == -1 else "run_right")
