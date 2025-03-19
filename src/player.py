import pygame
import random
from settings import PLAYER_SPEED, PLAYER_JUMP, GRAVITY, TILE_SIZE, EFFECTS_VOLUME

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Player animations
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
            "hit_left": self.load_animation("assets/images/player/hit_left_spritesheet.png", 312, 232, 4),
            "hit_right": self.load_animation("assets/images/player/hit_right_spritesheet.png", 312, 232, 4),
            "door_in": self.load_animation("assets/images/player/door_in.png", 312, 232, 8),
            "dead": self.load_animation("assets/images/player/dead_spritesheet.png", 312, 232, 4)
        }

        # Player health
        self.health = 3
        self.max_health = 3
        self.dead = False
        self.death_anim_done = False

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
        self.attack_duration = 500  # Attack lasts 500ms
        self.attack_start_time = 0

        # Immunity state after taking damage
        self.immune = False
        self.immune_timer = 0  # Time when immunity starts
        self.immune_duration = 1000  # 1 second of immunity

        # Knockback properties
        self.knockback = False
        self.knockback_timer = 0
        self.knockback_duration = 500  # 0.5 seconds
        self.knockback_force_x = 8  # Horizontal knockback force
        self.knockback_force_y = -10  # Vertical knockback force

        # Hurt state (for playing the hit animation)
        self.hurt = False
        self.hurt_timer = 0
        self.hurt_duration = 600  # Adjust duration to match hit animation length

        # Door entry flags
        self.door_entry = False
        self.door_in_anim_done = False

        # Animation timing
        self.last_update = pygame.time.get_ticks()
        # For running sound: prevent spamming by using a timer
        self.last_run_sound_time = pygame.time.get_ticks()

        # -------------------------------
        # NEW: Load sound assets for the player
        # Effects volume is a fraction (0.0 - 1.0)
        vol = EFFECTS_VOLUME / 10.0
        self.sounds = {}
        # Run step sounds (randomized)
        self.sounds["run"] = [
            pygame.mixer.Sound("assets/sounds/player/steps/step_cloth1.ogg"),
            pygame.mixer.Sound("assets/sounds/player/steps/step_cloth2.ogg"),
            pygame.mixer.Sound("assets/sounds/player/steps/step_cloth3.ogg"),
            pygame.mixer.Sound("assets/sounds/player/steps/step_cloth4.ogg")
        ]
        for s in self.sounds["run"]:
            s.set_volume(vol)
        # Jump sound
        self.sounds["jump"] = pygame.mixer.Sound("assets/sounds/player/jump.ogg")
        self.sounds["jump"].set_volume(vol)
        # Attack sounds (randomized)
        self.sounds["attack"] = [
            pygame.mixer.Sound("assets/sounds/player/attack/1.wav"),
            pygame.mixer.Sound("assets/sounds/player/attack/2.wav"),
            pygame.mixer.Sound("assets/sounds/player/attack/3.wav"),
            pygame.mixer.Sound("assets/sounds/player/attack/4.wav"),
            pygame.mixer.Sound("assets/sounds/player/attack/5.wav")
        ]
        for s in self.sounds["attack"]:
            s.set_volume(vol/2)
        # Damaged sounds (randomized)
        self.sounds["damaged"] = [
            pygame.mixer.Sound("assets/sounds/player/damaged/hit1.ogg"),
            pygame.mixer.Sound("assets/sounds/player/damaged/hit3.ogg"),
            pygame.mixer.Sound("assets/sounds/player/damaged/hit5.ogg")
        ]
        for s in self.sounds["damaged"]:
            s.set_volume(vol)
        # Dead sound (played once)
        self.sounds["dead"] = pygame.mixer.Sound("assets/sounds/player/dead.ogg")
        self.sounds["dead"].set_volume(vol)
        # -------------------------------

    def update_hitbox(self):
        """Ensure the hitbox follows the player correctly."""
        self.hitbox.topleft = (self.rect.x + 110, self.rect.y + 56)

    def load_animation(self, path, frame_width, frame_height, num_frames):
        """Load spritesheet and extract frames."""
        sheet = pygame.image.load(path).convert_alpha()
        return [sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                for i in range(num_frames)]

    def set_animation(self, animation):
        """Change animation if different from current."""
        # Prevent changing animation if the player is hurt (except for hit animations)
        if self.hurt and animation not in ["hit_left", "hit_right"]:
            return
        if self.current_animation != animation:
            self.current_animation = animation
            self.frame_index = 0

    def attack(self):
        """Triggers attack animation but allows movement."""
        if not self.attacking:
            self.play_attack_sound()
            self.attacking = True
            self.attack_start_time = pygame.time.get_ticks()
            # Set attack animation based on direction
            if self.last_direction == "right":
                self.set_animation("attack_right")
            else:
                self.set_animation("attack_left")
            self.frame_index = 0
            self.image = self.animations[self.current_animation][self.frame_index]  # Force first frame

    def start_door_entry(self):
        """Trigger door entry: play door_in sound and animation."""
        self.door_entry = True
        self.set_animation("door_in")
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()


    def attack_hitbox(self):
        attack_width = 80  # Adjust based on attack range
        attack_height = 50  # Adjust height if needed
        if self.last_direction == "right":
            return pygame.Rect(self.hitbox.right, self.hitbox.top, attack_width, attack_height)
        else:
            return pygame.Rect(self.hitbox.left - attack_width, self.hitbox.top, attack_width, attack_height)

    def take_damage(self, source=None, invuln_duration=None):
        # If already dead, do nothing.
        if self.dead:
            return
        if invuln_duration is None:
            invuln_duration = 1000 if source == "bomb" else 500
        # If health is 1, then a hit causes death.
        if self.health == 1:
            self.health = 0
            self.dead = True
            self.set_animation("dead")
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()
            self.play_dead_sound()
            return
        else:
            self.health -= 1
            self.immune = True
            self.immune_timer = pygame.time.get_ticks()
            self.knockback = True
            self.knockback_timer = pygame.time.get_ticks()
            self.hurt = True
            self.hurt_timer = pygame.time.get_ticks()
            if self.last_direction == "right":
                self.vel_x = -self.knockback_force_x
                self.set_animation("hit_right")
            else:
                self.vel_x = self.knockback_force_x
                self.set_animation("hit_left")
            self.vel_y = self.knockback_force_y
            self.immune_duration = invuln_duration
            self.play_damaged_sound()

    def update_animation(self):
        """Update player's animation without interrupting attack, knockback, or damage animations."""
        now = pygame.time.get_ticks()
        if self.dead:
            if now - self.last_update > 100:
                self.last_update = now
                if self.frame_index < len(self.animations["dead"]) - 1:
                    self.frame_index += 1
                else:
                    self.death_anim_done = True
                self.image = self.animations["dead"][self.frame_index]
            return
        if self.door_entry:
            if now - self.last_update > 100:
                self.last_update = now
                if self.frame_index < len(self.animations["door_in"]) - 1:
                    self.frame_index += 1
                else:
                    self.door_in_anim_done = True
                self.image = self.animations["door_in"][self.frame_index]
            return
        if self.hurt:
            if now - self.hurt_timer > self.hurt_duration:
                self.hurt = False
                self.set_animation("idle_right" if self.last_direction == "right" else "idle_left")
            else:
                if now - self.last_update > 200:
                    self.last_update = now
                    self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_animation])
                    self.image = self.animations[self.current_animation][self.frame_index]
            return
        if self.knockback:
            if now - self.knockback_timer > self.knockback_duration:
                self.knockback = False
                self.vel_x = 0
            return
        if self.attacking:
            if now - self.attack_start_time > self.attack_duration:
                self.attacking = False
        if now - self.last_update > 100:
            self.last_update = now
            if self.attacking:
                if self.frame_index < len(self.animations[self.current_animation]) - 1:
                    self.frame_index += 1
                else:
                    self.attacking = False
                    self.set_animation("idle_right" if self.last_direction == "right" else "idle_left")
            else:
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_animation])
            self.image = self.animations[self.current_animation][self.frame_index]

    def handle_input(self):
        """Handles movement and attack input."""
        if self.knockback or self.door_entry:
            return
        keys = pygame.key.get_pressed()
        if not self.attacking:
            self.vel_x = 0
            if keys[pygame.K_LEFT]:
                self.vel_x = -PLAYER_SPEED
                self.last_direction = "left"
            if keys[pygame.K_RIGHT]:
                self.vel_x = PLAYER_SPEED
                self.last_direction = "right"
            if keys[pygame.K_UP]:
                if not self.jump_pressed:
                    if self.on_ground:
                        self.vel_y = -PLAYER_JUMP
                        self.on_ground = False
                        self.can_double_jump = True
                        self.play_jump_sound()  # Play jump sound when jumping from ground
                    elif self.can_double_jump:
                        self.vel_y = -PLAYER_JUMP
                        self.can_double_jump = False
                        self.play_jump_sound()  # Play jump sound for double jump as well
                    self.jump_pressed = True
            else:
                self.jump_pressed = False
        if keys[pygame.K_SPACE]:
            self.attack()

    def apply_gravity(self):
        """Apply gravity to player."""
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10

    def move_and_collide(self, dx, dy, blocks):
        """Handle movement and collisions."""
        self.hitbox.x += dx
        for block in blocks:
            if self.hitbox.colliderect(block.rect):
                if dx > 0:
                    self.hitbox.right = block.rect.left
                if dx < 0:
                    self.hitbox.left = block.rect.right
        self.rect.x = self.hitbox.x - 110

        was_on_ground = self.on_ground
        self.on_ground = False
        self.hitbox.y += dy
        for block in blocks:
            if self.hitbox.colliderect(block.rect):
                if dy > 0:
                    self.hitbox.bottom = block.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.can_double_jump = True
                if dy < 0:
                    self.hitbox.top = block.rect.bottom
                    self.vel_y = 0
        self.rect.y = self.hitbox.y - 56

    def update(self, blocks, bombs, enemies):
        """Update player state, movement, animations, and handle bomb collisions."""
        self.handle_input()
        self.apply_gravity()
        self.move_and_collide(self.vel_x, self.vel_y, blocks)

        # Play running sound if on ground and moving with a delay
        if self.on_ground and self.vel_x != 0:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_run_sound_time > 300:
                self.play_run_sound()
                self.last_run_sound_time = current_time

        for bomb in bombs:
            if bomb.exploding and bomb.frame_index == 0 and self.hitbox.colliderect(bomb.explosion_rect):
                if not self.immune:
                    self.take_damage(source="bomb", invuln_duration=1000)

        if self.immune and pygame.time.get_ticks() - self.immune_timer > self.immune_duration:
            self.immune = False
        if self.knockback and pygame.time.get_ticks() - self.knockback_timer > self.knockback_duration:
            self.knockback = False
            self.vel_x = 0

        if self.attacking:
            for enemy in enemies:
                if self.attack_hitbox().colliderect(enemy.hitbox):
                    enemy.take_damage()
                    if hasattr(enemy, "play_damaged_sound"):
                        enemy.play_damaged_sound()

        if not self.attacking:
            if self.on_ground:
                if self.vel_x > 0:
                    self.set_animation("run_right")
                elif self.vel_x < 0:
                    self.set_animation("run_left")
                else:
                    self.set_animation("idle_right" if self.last_direction == "right" else "idle_left")
            else:
                if self.vel_y < 0:
                    self.set_animation("jump_right" if self.last_direction == "right" else "jump_left")
                else:
                    self.set_animation("fall_right" if self.last_direction == "right" else "fall_left")

        self.update_animation()
        self.update_hitbox()


    def play_run_sound(self):
        import settings
        sound = random.choice(self.sounds["run"])
        sound.set_volume(settings.EFFECTS_VOLUME / 10.0)
        sound.play()

    def play_jump_sound(self):
        import settings
        self.sounds["jump"].set_volume(settings.EFFECTS_VOLUME / 10.0)
        self.sounds["jump"].play()
    def play_attack_sound(self):
        import settings
        sound = random.choice(self.sounds["attack"])
        sound.set_volume(settings.EFFECTS_VOLUME / 10.0/2)
        sound.play()

    def play_damaged_sound(self):
        import settings
        sound = random.choice(self.sounds["damaged"])
        sound.set_volume(settings.EFFECTS_VOLUME / 10.0)
        sound.play()

    def play_dead_sound(self):
        import settings
        self.sounds["dead"].set_volume(settings.EFFECTS_VOLUME / 10.0)
        self.sounds["dead"].play()

