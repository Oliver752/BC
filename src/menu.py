import pygame
import sys
import json
import os
from settings import *
from blocks import Block
from player import Player
from enemy import BomberPig, Pig, King
from camera import Camera
from collectables import Collectable, Heart
from level_editor import run_editor


# Helper function for collision detection
def hitbox_collide(player, collectable):
    return player.hitbox.colliderect(collectable.rect)

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 50)
        self.input_font = pygame.font.Font(None, 40)
        self.options = ["Play", "Sandbox", "Settings", "Quit"]
        self.selected_index = 0

        # HUD assets
        self.diamond_icon = pygame.image.load("assets/images/hud/diamond.png").convert_alpha()
        self.diamond_icon = pygame.transform.scale(self.diamond_icon, (32, 32))
        self.healthbar = pygame.image.load("assets/images/hud/healthbar.png").convert_alpha()
        self.healthbar = pygame.transform.scale(self.healthbar, (198, 102))
        self.hud_heart = pygame.image.load("assets/images/hud/heart.png").convert_alpha()
        self.hud_heart = pygame.transform.scale(self.hud_heart, (30, 25))

        # Diamond count resets each level
        self.diamond_count = 0

        # Track current level/folder so we can restart
        self.current_level = None
        self.current_folder = None

    def draw_menu(self):
        self.screen.fill(BG_COLOR)
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.selected_index else (200, 200, 200)
            text_surface = self.font.render(option, True, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 60))
            self.screen.blit(text_surface, text_rect)

    def main_menu(self):
        while True:
            self.draw_menu()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        choice = self.options[self.selected_index]
                        if choice == "Play":
                            # Loads from levels/default
                            self.level_select(folder="default")
                        elif choice == "Sandbox":
                            self.sandbox_menu()
                        elif choice == "Settings":
                            self.settings_menu()
                        elif choice == "Quit":
                            pygame.quit()
                            sys.exit()
            self.clock.tick(FPS)

    def sandbox_menu(self):
        options = ["Create New", "Browse Levels", "Back"]
        selected_option = 0
        while True:
            self.screen.fill(BG_COLOR)
            for i, option in enumerate(options):
                color = (255, 255, 255) if i == selected_option else (200, 200, 200)
                text_surface = self.font.render(option, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 60))
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        choice = options[selected_option]
                        if choice == "Back":
                            return
                        elif choice == "Create New":
                            self.create_new_level(folder="sandbox")
                        elif choice == "Browse Levels":
                            self.browse_levels(folder="sandbox")
            self.clock.tick(FPS)

    def browse_levels(self, folder="sandbox"):
        folder_path = os.path.join("levels", folder)
        all_files = os.listdir(folder_path)
        level_names = []
        for f in all_files:
            if f.endswith(".json"):
                # Strip the .json extension
                base_name = f[:-5]
                level_names.append(base_name)

        # Add a "Back" option at the bottom
        level_names.append("Back")

        if not level_names:
            return  # or show a message, etc.

        selected_index = 0
        while True:
            self.screen.fill(BG_COLOR)

            # Draw the list of levels plus the "Back" option
            for i, lvl in enumerate(level_names):
                color = (255, 255, 255) if i == selected_index else (200, 200, 200)
                text_surface = self.font.render(lvl, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 60))
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(level_names)
                    elif event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(level_names)
                    elif event.key == pygame.K_RETURN:
                        chosen_level = level_names[selected_index]
                        # If the user chooses "Back," return to sandbox menu
                        if chosen_level == "Back":
                            return
                        else:
                            self.sandbox_sub_menu(chosen_level, folder)
                    elif event.key == pygame.K_ESCAPE:
                        return

    def sandbox_sub_menu(self, level_name, folder="sandbox"):
        options = ["Play", "Edit", "Back"]
        selected_option = 0
        while True:
            self.screen.fill(BG_COLOR)
            for i, opt in enumerate(options):
                color = (255, 255, 255) if i == selected_option else (200, 200, 200)
                text_surface = self.font.render(opt, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 60))
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        choice = options[selected_option]
                        if choice == "Back":
                            return  # Go back to the list of levels
                        elif choice == "Play":
                            # Remember: load_level expects a .json filename
                            self.load_level(level_name + ".json", folder=folder)
                            return
                        elif choice == "Edit":
                            # Call your new level editor
                            run_editor(self.screen, level_name, folder)

                            # After editing, we can either return to this sub-menu
                            # or go back to the browse list. Here, let's just return:
                            return
                    elif event.key == pygame.K_ESCAPE:
                        return

    def load_level(self, filename, folder="default"):
        """
        Loads the given level from either levels/default or levels/sandbox.
        """
        self.current_level = filename
        self.current_folder = folder

        with open(f"levels/{folder}/{filename}", 'r') as file:
            data = json.load(file)

        all_sprites = pygame.sprite.Group()
        blocks = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        collectables = pygame.sprite.Group()

        player = None
        for row_index, row in enumerate(data["level"]):
            for col_index, tile in enumerate(row):
                x, y = col_index * TILE_SIZE, row_index * TILE_SIZE
                if tile == "G":
                    block = Block(x, y, "grass")
                    blocks.add(block)
                    all_sprites.add(block)
                elif tile == "D":
                    block = Block(x, y, "dirt")
                    blocks.add(block)
                    all_sprites.add(block)
                elif tile == "S":
                    block = Block(x, y, "stone")
                    blocks.add(block)
                    all_sprites.add(block)
                elif tile == "P":
                    player = Player(x, y)
                    all_sprites.add(player)
                elif tile == "C":
                    c = Collectable(x, y)
                    collectables.add(c)
                    all_sprites.add(c)
                elif tile == "H":
                    heart = Heart(x, y)
                    collectables.add(heart)
                    all_sprites.add(heart)
                elif tile == "B":
                    enemy = BomberPig(x, y)
                    enemies.add(enemy)
                    all_sprites.add(enemy)
                elif tile == "E":
                    enemy = Pig(x, y)
                    enemies.add(enemy)
                    all_sprites.add(enemy)
                elif tile == "K":
                    enemy = King(x, y)
                    enemies.add(enemy)
                    all_sprites.add(enemy)

        # Setup camera
        self.camera = Camera(
            SCREEN_WIDTH, SCREEN_HEIGHT,
            len(data["level"][0]) * TILE_SIZE,
            len(data["level"]) * TILE_SIZE
        )

        self.diamond_count = 0
        self.run_level(all_sprites, player, blocks, collectables, enemies)

    def run_level(self, all_sprites, player, blocks, collectables, enemies):
        """
        Runs the game level, handling updates, drawing, interactions.
        Press ESC for a pause menu (resume, restart, settings, leave).
        """
        bombs = pygame.sprite.Group()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        result = self.pause_menu()
                        if result == "resume":
                            pass
                        elif result == "restart":
                            # Reload same level
                            self.load_level(self.current_level, folder=self.current_folder)
                            return
                        elif result == "settings":
                            self.settings_menu()
                        elif result == "leave":
                            # leave to main menu
                            return

            # Update
            player.update(blocks, bombs, enemies)
            collectables.update()
            bombs.update(blocks, player)

            # Update enemies
            for enemy in enemies:
                if isinstance(enemy, BomberPig):
                    enemy.update(player, blocks, bombs)
                elif isinstance(enemy, Pig):
                    enemy.update(player, blocks)
                elif isinstance(enemy, King):
                    enemy.update(player, blocks)

            # Collisions with collectibles
            collected = pygame.sprite.spritecollide(player, collectables, False, collided=hitbox_collide)
            for collectible in collected:
                if collectible.state != "disappear":
                    if isinstance(collectible, Heart):
                        if player.health < player.max_health:
                            collectible.collect()
                            player.health += 1
                    else:
                        collectible.collect()
                        self.diamond_count += 1

            # Camera & draw
            self.camera.update(player)
            self.screen.fill(BG_COLOR)
            for sprite in all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
            for bomb in bombs:
                self.screen.blit(bomb.image, self.camera.apply(bomb))
            """
            # Show debug for King if desired
            for enemy in enemies:
                if isinstance(enemy, King) and getattr(enemy, "debug", False):
                    enemy.draw_debug(self.screen, self.camera)
            """
            # HUD
            hud_offset = 10
            self.screen.blit(self.healthbar, (hud_offset, hud_offset))
            healthbar_height = self.healthbar.get_height()
            start_x = hud_offset + 51
            start_y = hud_offset + (healthbar_height - 25) // 2
            for i in range(player.max_health):
                heart_x = start_x + i * (32 + 1)
                if i < player.health:
                    self.screen.blit(self.hud_heart, (heart_x, start_y))

            icon_rect = self.diamond_icon.get_rect(topright=(SCREEN_WIDTH - hud_offset, hud_offset))
            self.screen.blit(self.diamond_icon, icon_rect)
            count_text = self.font.render(str(self.diamond_count), True, (255, 255, 255))
            text_rect = count_text.get_rect(midright=(icon_rect.left - 5, icon_rect.centery))
            self.screen.blit(count_text, text_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

    def pause_menu(self):
        """
        Semi-transparent overlay with:
          - Resume
          - Restart
          - Settings
          - Leave
        Returns "resume", "restart", "settings", or "leave"
        """
        options = ["Resume", "Restart", "Settings", "Leave"]
        selected_index = 0
        paused = True

        while paused:
            # Draw a semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((100, 206, 235, 150))  # black, alpha=150
            self.screen.blit(overlay, (0, 0))

            # Draw menu options
            for i, option in enumerate(options):
                color = (255, 255, 255) if i == selected_index else (200, 200, 200)
                text_surface = self.font.render(option, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 60))
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        return options[selected_index].lower()  # "resume","restart","settings","leave"
                    elif event.key == pygame.K_ESCAPE:
                        return "resume"

    def level_select(self, folder="default"):
        levels = ["Level 1", "Back"]
        selected_level = 0
        while True:
            self.screen.fill(BG_COLOR)
            for i, level in enumerate(levels):
                color = (255, 255, 255) if i == selected_level else (200, 200, 200)
                text_surface = self.font.render(level, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 60))
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_level = (selected_level + 1) % len(levels)
                    elif event.key == pygame.K_UP:
                        selected_level = (selected_level - 1) % len(levels)
                    elif event.key == pygame.K_RETURN:
                        choice = levels[selected_level]
                        if choice == "Back":
                            return
                        elif choice == "Level 1":
                            # Hard-coded example, from levels/default
                            self.load_level("level1.json", folder=folder)
                            return
            self.clock.tick(FPS)

    def create_new_level(self, folder="default"):

        sizes = ["20x11", "25x14", "30x17", "35x20", "40x22", "Back"]
        selected_size = 0
        while True:
            self.screen.fill(BG_COLOR)
            for i, size in enumerate(sizes):
                color = (255, 255, 255) if i == selected_size else (200, 200, 200)
                text_surface = self.font.render(size, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 60))
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_size = (selected_size + 1) % len(sizes)
                    elif event.key == pygame.K_UP:
                        selected_size = (selected_size - 1) % len(sizes)
                    elif event.key == pygame.K_RETURN:
                        choice = sizes[selected_size]
                        if choice == "Back":
                            return
                        # Otherwise it's a size
                        width, height = map(int, choice.split('x'))
                        name = self.get_input("Enter level name:")
                        self.create_empty_level(name, width, height, folder=folder)
                        return

    def get_input(self, prompt):
        input_text = ""
        while True:
            self.screen.fill(BG_COLOR)
            prompt_surface = self.input_font.render(prompt, True, (255, 255, 255))
            input_surface = self.input_font.render(input_text, True, (255, 255, 255))
            self.screen.blit(prompt_surface, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(input_surface, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return input_text
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isalnum() or event.unicode in ('_', '-'):
                        input_text += event.unicode

    def create_empty_level(self, name, width, height, folder="default"):
        level = [["." for _ in range(width)] for _ in range(height)]
        level[0] = ["G"] * width
        level[-1] = ["S"] * width
        for row in level:
            row[0] = "G"
            row[-1] = "G"
        level[-3][3] = "P"
        tiles = {
            "G": "grass",
            "S": "stone",
            ".": "empty",
            "P": "player",
            "C": "collectable",
            "B": "bomber",
            "E": "pig_enemy",
            "K": "king_pig"
        }
        data = {"level": level, "tiles": tiles}
        os.makedirs(f'levels/{folder}', exist_ok=True)
        with open(f"levels/{folder}/{name}.json", 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Level {name} created in levels/{folder}.")

    def load_existing_level(self, folder="default"):
        """
        Show the .json levels plus a "Back" option to return to sandbox menu.
        """
        path = f'levels/{folder}'
        if not os.path.isdir(path):
            print(f"No directory found: {path}")
            return

        levels = [f for f in os.listdir(path) if f.endswith('.json')]
        if not levels:
            print("No levels found in", path)
            return

        # Add a "Back" option
        levels.append("Back")
        selected_level = 0
        while True:
            self.screen.fill(BG_COLOR)
            for i, level in enumerate(levels):
                color = (255, 255, 255) if i == selected_level else (200, 200, 200)
                text_surface = self.font.render(level, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 60))
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_level = (selected_level + 1) % len(levels)
                    elif event.key == pygame.K_UP:
                        selected_level = (selected_level - 1) % len(levels)
                    elif event.key == pygame.K_RETURN:
                        choice = levels[selected_level]
                        if choice == "Back":
                            return
                        self.load_level(choice, folder=folder)
                        return

    def settings_menu(self):
        """
        Basic settings menu with just a 'Back' option for now.
        """
        options = ["Back"]
        selected_option = 0
        while True:
            self.screen.fill(BG_COLOR)
            for i, option in enumerate(options):
                color = (255, 255, 255) if i == selected_option else (200, 200, 200)
                text_surface = self.font.render(option, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 60))
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        # Only 'Back' for now
                        return
            self.clock.tick(FPS)
