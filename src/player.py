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
        self.attack_duration = 500  # Attack lasts 300ms
        self.attack_start_time = 0
        # Immunity state after taking damage
        self.immune = False
        self.immune_timer = 0  # Stores the time when immunity starts
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

    def update_hitbox(self):
        """Ensure the hitbox follows the player correctly."""
        self.hitbox.topleft = (self.rect.x + 110, self.rect.y + 56)

    def load_animation(self, path, frame_width, frame_height, num_frames):
        """Load spritesheet and extract frames."""
        sheet = pygame.image.load(path).convert_alpha()
        return [sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)) for i in range(num_frames)]

    def set_animation(self, animation):
        """Change animation if different from current."""
        #  Prevent changing animation if the player is hurt
        if self.hurt and animation not in ["hit_left", "hit_right"]:
            return

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
    def start_door_entry(self):
        """Trigger door entry: play door_in animation."""
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

    def update_animation(self):
        """Update player's animation without interrupting attack, knockback, or damage animations."""
        now = pygame.time.get_ticks()
        # If the player is dead, update the dead animation
        if self.dead:
            if now - self.last_update > 100:  # adjust frame speed if needed
                self.last_update = now
                if self.frame_index < len(self.animations["dead"]) - 1:
                    self.frame_index += 1
                else:
                    self.death_anim_done = True
                self.image = self.animations["dead"][self.frame_index]
            return
        # If door entry is active, update door_in animation and mark when finished
        if self.door_entry:
            if now - self.last_update > 100:
                self.last_update = now
                if self.frame_index < len(self.animations["door_in"]) - 1:
                    self.frame_index += 1
                else:
                    self.door_in_anim_done = True
                self.image = self.animations["door_in"][self.frame_index]
            return
        #  Ensure the hit animation plays fully before switching back
        if self.hurt:
            if now - self.hurt_timer > self.hurt_duration:
                self.hurt = False  #  End hit animation after duration
                self.set_animation("idle_right" if self.last_direction == "right" else "idle_left")
            else:
                #  Play the hit animation (loop between 2 frames)
                if now - self.last_update > 200:  # Adjust speed if needed
                    self.last_update = now
                    self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_animation])
                    self.image = self.animations[self.current_animation][self.frame_index]
            return  #  Prevent other animations from playing while hurt

        #  Ensure knockback animation plays before other animations
        if self.knockback:
            if now - self.knockback_timer > self.knockback_duration:
                self.knockback = False  #  End knockback after duration
                self.vel_x = 0  # Stop horizontal movement after knockback ends
            return  #  Prevent other animations from playing while knocked back

        #  Continue normal animation updates
        if self.attacking:
            if now - self.attack_start_time > self.attack_duration:
                self.attacking = False  # End attack after duration

        if now - self.last_update > 100:  # Adjust frame speed
            self.last_update = now

            if self.attacking:
                if self.frame_index < len(self.animations[self.current_animation]) - 1:
                    self.frame_index += 1
                else:
                    self.attacking = False  # Attack animation finished
                    self.set_animation("idle_right" if self.last_direction == "right" else "idle_left")
            else:
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.current_animation])

            self.image = self.animations[self.current_animation][self.frame_index]

    def handle_input(self):
        """Handles movement and attack input."""
        if self.knockback:  #  Disable input during knockback
            return
        # Disable input if in door entry sequence
        if self.door_entry:
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

            # Handle jumping
            if keys[pygame.K_UP]:
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

    def update(self, blocks, bombs, enemies):
        """Update player state, movement, animations, and handle bomb collisions."""
        self.handle_input()
        self.apply_gravity()
        self.move_and_collide(self.vel_x, self.vel_y, blocks)

        #  Check for bomb collisions (only on the first frame & if not immune)
        # Check for bomb collisions (only on the first frame & if not immune)
        for bomb in bombs:
            if bomb.exploding and bomb.frame_index == 0 and self.hitbox.colliderect(bomb.explosion_rect):
                if not self.immune:
                    self.take_damage(source="bomb", invuln_duration=1000)

        #  Reset immunity after 1 second
        if self.immune:
            if pygame.time.get_ticks() - self.immune_timer > self.immune_duration:
                self.immune = False  #  Reset immunity after 1 second
        #  Handle knockback duration
        if self.knockback:
            if pygame.time.get_ticks() - self.knockback_timer > self.knockback_duration:
                self.knockback = False  #  End knockback after duration
                self.vel_x = 0  # Stop horizontal movement after knockback ends
        if self.attacking:
            for enemy in enemies:  # Loop through all enemies
                if self.attack_hitbox().colliderect(enemy.hitbox):  # Check if attack hits
                    enemy.take_damage()  #  Apply damage to the enemy
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
                if self.vel_y < 0:
                    self.set_animation("jump_right" if self.last_direction == "right" else "jump_left")
                else:
                    self.set_animation("fall_right" if self.last_direction == "right" else "fall_left")

        self.update_animation()
        self.update_hitbox()




