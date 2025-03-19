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

        # Default main menu options
        self.options = ["Play", "Sandbox", "Settings", "Quit"]
        self.selected_index = 0

        # Load a button image for all menus
        self.button_img = pygame.image.load("assets/images/btn/button300.png").convert_alpha()
        self.button_width = self.button_img.get_width()
        self.button_height = self.button_img.get_height()

        # HUD assets
        self.diamond_icon = pygame.image.load("assets/images/hud/diamond.png").convert_alpha()
        self.diamond_icon = pygame.transform.scale(self.diamond_icon, (32, 32))
        self.healthbar = pygame.image.load("assets/images/hud/healthbar.png").convert_alpha()
        self.healthbar = pygame.transform.scale(self.healthbar, (198, 102))
        self.hud_heart = pygame.image.load("assets/images/hud/heart.png").convert_alpha()
        self.hud_heart = pygame.transform.scale(self.hud_heart, (30, 25))
        self.game_bg = pygame.image.load("assets/images/hud/gamebg.jpg").convert()
        self.game_bg = pygame.transform.scale(self.game_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.menu_bg = pygame.image.load("assets/images/hud/menubg.jpg").convert()
        self.menu_bg = pygame.transform.scale(self.menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.title_img = pygame.image.load("assets/images/hud/title.png").convert_alpha()
        self.pause_bg = pygame.image.load("assets/images/hud/pausebg.png").convert()
        self.pause_bg = pygame.transform.scale(self.pause_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        # Diamond count resets each level
        self.diamond_count = 0

        # Track current level/folder so we can restart
        self.current_level = None
        self.current_folder = None

    def draw_menu_buttons(self, options, selected_index, start_y=200, spacing=80):
        """
        Draws each option as a button image with text on top, stacked vertically.
        :options: list of strings
        :selected_index: which option is highlighted
        :start_y: vertical start position
        :spacing: vertical space between buttons
        """
        for i, text in enumerate(options):
            # Button position
            x = SCREEN_WIDTH // 2 - self.button_width // 2
            y = start_y + i * (self.button_height + spacing)

            # Draw the button image
            rect = pygame.Rect(x, y, self.button_width, self.button_height)
            self.screen.blit(self.button_img, rect)

            # Highlight text color if this is the selected option
            color = (128, 128, 128) if i == selected_index else (0, 0, 0)
            surf = self.font.render(text, True, color)
            surf_rect = surf.get_rect(center=rect.center)
            self.screen.blit(surf, surf_rect)

    def main_menu(self):
        options = ["Play", "Sandbox", "Settings", "Quit"]
        selected = 0
        while True:
            # Blit the menu background first (if using a background image)
            self.screen.blit(self.menu_bg, (0, 0))

            # Position the title centered horizontally and 350px from the top
            title_rect = self.title_img.get_rect(midtop=(SCREEN_WIDTH // 2, 130))
            self.screen.blit(self.title_img, title_rect)

            # Draw menu
            self.draw_menu_buttons(options, selected, start_y=250, spacing=20)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        choice = options[selected]
                        if choice == "Play":
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
        options = ["Create", "Browse", "Back"]
        selected = 0
        while True:
            self.screen.blit(self.menu_bg, (0, 0))
            self.draw_menu_buttons(options, selected, start_y=250, spacing=20)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        choice = options[selected]
                        if choice == "Back":
                            return
                        elif choice == "Create":
                            self.create_new_level(folder="sandbox")
                        elif choice == "Browse":
                            self.browse_levels(folder="sandbox")
            self.clock.tick(FPS)

    def browse_levels(self, folder="sandbox"):
        folder_path = os.path.join("levels", folder)
        all_files = os.listdir(folder_path)
        level_names = [f[:-5] for f in all_files if f.endswith(".json")]
        # Add a "Back" option at the bottom
        level_names.append("Back")
        if not level_names:
            return  # or show a message, etc.

        selected = 0
        while True:
            self.screen.blit(self.pause_bg, (0, 0))
            self.draw_menu_buttons(level_names, selected, start_y=200, spacing=20)
            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(level_names)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(level_names)
                    elif event.key == pygame.K_RETURN:
                        chosen_level = level_names[selected]
                        if chosen_level == "Back":
                            return
                        else:
                            self.sandbox_sub_menu(chosen_level, folder)
                    elif event.key == pygame.K_ESCAPE:
                        return

    def sandbox_sub_menu(self, level_name, folder="sandbox"):
        options = ["Play", "Edit", "Back"]
        selected = 0
        while True:
            self.screen.blit(self.pause_bg, (0, 0))
            self.draw_menu_buttons(options, selected, start_y=300, spacing=20)
            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        choice = options[selected]
                        if choice == "Back":
                            return
                        elif choice == "Play":
                            self.load_level(level_name + ".json", folder=folder)
                            return
                        elif choice == "Edit":
                            run_editor(self.screen, level_name, folder)
                            return
                    elif event.key == pygame.K_ESCAPE:
                        return

    def load_level(self, filename, folder="default"):
        self.current_level = filename
        self.current_folder = folder

        with open(f"levels/{folder}/{filename}", 'r') as file:
            data = json.load(file)

        all_sprites = pygame.sprite.Group()
        blocks = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        collectables = pygame.sprite.Group()
        door_group = pygame.sprite.Group()
        player = None
        required_gems = sum(row.count("C") for row in data["level"])
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
                elif tile == "F":
                    from door import Door
                    door = Door(x, y, required_gems)
                    door_group.add(door)

        self.camera = Camera(
            SCREEN_WIDTH, SCREEN_HEIGHT,
            len(data["level"][0]) * TILE_SIZE,
            len(data["level"]) * TILE_SIZE
        )

        self.diamond_count = 0
        # Corrected: pass door_group as an argument
        self.run_level(all_sprites, player, blocks, collectables, enemies, door_group)

    def run_level(self, all_sprites, player, blocks, collectables, enemies, door_group):
        bombs = pygame.sprite.Group()
        running = True

        while running:
            keys = pygame.key.get_pressed()
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
                            self.load_level(self.current_level, folder=self.current_folder)
                            return
                        elif result == "settings":
                            self.settings_menu()
                        elif result == "leave":
                            return

            player.update(blocks, bombs, enemies)
            collectables.update()
            bombs.update(blocks, player)

            # Update enemies
            for enemy in enemies:
                if hasattr(enemy, 'throw_bomb'):
                    enemy.update(player, blocks, bombs)
                else:
                    enemy.update(player, blocks)

            # Handle collisions with collectibles
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

            # Update doors
            for door in door_group:
                door.update(self.diamond_count, player, keys)

            # Update camera
            self.camera.update(player)
            self.screen.blit(self.game_bg, (0, 0))

            # Draw door images first (behind player)
            for door in door_group:
                door.draw_image(self.screen, self.camera)

            # Draw all sprites (player, blocks, etc.)
            for sprite in all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
            for bomb in bombs:
                self.screen.blit(bomb.image, self.camera.apply(bomb))

            # Draw door UI bubble on top
            for door in door_group:
                door.draw_ui(self.screen, self.font, self.diamond_count, self.camera)

            # Draw HUD
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
            if player.dead and player.death_anim_done:
                self.lost_menu()
                running = False

            if player.door_entry and player.door_in_anim_done:
                self.level_complete_menu()
                running = False

    def pause_menu(self):
        options = ["Resume", "Restart", "Settings", "Leave"]
        selected = 0
        paused = True

        while paused:
            # Semi-transparent overlay
            self.screen.blit(self.pause_bg, (0, 0))

            # Draw menu
            self.draw_menu_buttons(options, selected, start_y=300, spacing=20)
            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        return options[selected].lower()  # "resume","restart","settings","leave"
                    elif event.key == pygame.K_ESCAPE:
                        return "resume"
    def level_complete_menu(self):
        options = ["Continue", "Leave"]
        selected = 0
        while True:
            self.screen.blit(self.pause_bg, (0, 0))
            complete_text = self.font.render("You beat the level", True, (255, 255, 255))
            self.screen.blit(complete_text, complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
            self.draw_menu_buttons(options, selected, start_y=SCREEN_HEIGHT // 2)
            pygame.display.flip()
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        choice = options[selected]
                        if choice == "Continue":
                            self.level_select(folder=self.current_folder)
                            return
                        elif choice == "Leave":
                            return
    def level_select(self, folder="default"):
        # Example "Level 1" plus "Back"
        levels = ["Level 1", "Back"]
        selected = 0
        while True:
            self.screen.blit(self.menu_bg, (0, 0))
            self.draw_menu_buttons(levels, selected, start_y=250, spacing=20)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(levels)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(levels)
                    elif event.key == pygame.K_RETURN:
                        choice = levels[selected]
                        if choice == "Back":
                            return
                        elif choice == "Level 1":
                            # Hard-coded example, from levels/default
                            self.load_level("level1.json", folder=folder)
                            return
            self.clock.tick(FPS)

    def create_new_level(self, folder="default"):
        # Allow holding down arrow keys for continuous changes
        pygame.key.set_repeat(200, 40)

        # Load images
        button_img = pygame.image.load("assets/images/btn/button.png").convert_alpha()  # 200x90
        field_img = pygame.image.load("assets/images/btn/field.png").convert_alpha()  # 200x90
        arrow_left_img = pygame.image.load("assets/images/btn/arrow_left.png").convert_alpha()
        arrow_right_img = pygame.image.load("assets/images/btn/arrow_right.png").convert_alpha()

        # Colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GRAY = (128, 128, 128)
        DISABLED = (70, 70, 70)

        # Ranges
        length_min, length_max = 30, 100
        height_min, height_max = 20, 50

        # State
        length = length_min
        height = height_min
        name_text = ""

        # Keyboard navigation items
        items = ["length", "height", "name", "create", "back"]
        active_index = 0

        # Vertical positions (adjust as you like)
        title_y = 80
        length_label_y = 240
        length_row_y = 280
        height_label_y = 370
        height_row_y = 320
        name_label_y = 510
        name_field_y = 480
        create_btn_y = 600
        back_btn_y = 700

        # For spacing arrow left / right ~80px from center
        ARROW_OFFSET = 80

        clock = pygame.time.Clock()

        while True:
            self.screen.blit(self.pause_bg, (0, 0))

            # --- Title ---
            title_surf = self.font.render("Create New Level", True, WHITE)
            self.screen.blit(
                title_surf,
                title_surf.get_rect(center=(SCREEN_WIDTH // 2, title_y))
            )

            # --- LENGTH ---
            # Label
            length_label_color = GRAY if items[active_index] == "length" else WHITE
            length_label_surf = self.input_font.render("Length", True, length_label_color)
            self.screen.blit(
                length_label_surf,
                length_label_surf.get_rect(center=(SCREEN_WIDTH // 2, length_label_y))
            )

            # Arrows & value
            left_rect_len = arrow_left_img.get_rect(midright=(SCREEN_WIDTH // 2 - ARROW_OFFSET, length_row_y))
            right_rect_len = arrow_right_img.get_rect(midleft=(SCREEN_WIDTH // 2 + ARROW_OFFSET, length_row_y))
            length_val_color = GRAY if items[active_index] == "length" else BLACK
            length_val_surf = self.input_font.render(str(length), True, length_val_color)
            length_val_rect = length_val_surf.get_rect(center=(SCREEN_WIDTH // 2, length_row_y))

            self.screen.blit(arrow_left_img, left_rect_len)
            self.screen.blit(length_val_surf, length_val_rect)
            self.screen.blit(arrow_right_img, right_rect_len)

            # --- HEIGHT ---
            # Label
            height_label_color = GRAY if items[active_index] == "height" else WHITE
            height_label_surf = self.input_font.render("Height", True, height_label_color)
            self.screen.blit(
                height_label_surf,
                height_label_surf.get_rect(center=(SCREEN_WIDTH // 2, height_label_y))
            )

            # Arrows & value (shift down)
            left_rect_h = arrow_left_img.get_rect(midright=(SCREEN_WIDTH // 2 - ARROW_OFFSET, height_row_y))
            left_rect_h.y += 100  # move below length row
            right_rect_h = arrow_right_img.get_rect(midleft=(SCREEN_WIDTH // 2 + ARROW_OFFSET, height_row_y))
            right_rect_h.y += 100
            height_val_color = GRAY if items[active_index] == "height" else BLACK
            height_val_surf = self.input_font.render(str(height), True, height_val_color)
            height_val_rect = height_val_surf.get_rect(center=(SCREEN_WIDTH // 2, height_row_y + 100))

            self.screen.blit(arrow_left_img, left_rect_h)
            self.screen.blit(height_val_surf, height_val_rect)
            self.screen.blit(arrow_right_img, right_rect_h)

            # --- NAME ---
            name_label_color = GRAY if items[active_index] == "name" else WHITE
            name_label_surf = self.input_font.render("Name", True, name_label_color)
            self.screen.blit(
                name_label_surf,
                name_label_surf.get_rect(center=(SCREEN_WIDTH // 2, name_label_y))
            )

            field_rect = field_img.get_rect(center=(SCREEN_WIDTH // 2, name_field_y))
            field_rect.y += 100  # place below height row
            self.screen.blit(field_img, field_rect)
            # typed text
            name_color = GRAY if items[active_index] == "name" else BLACK
            name_surf = self.input_font.render(name_text, True, name_color)
            name_surf_rect = name_surf.get_rect(center=field_rect.center)
            # Draw text centered without shifting
            self.screen.blit(name_surf, name_surf_rect)

            # --- CREATE BUTTON ---
            create_rect = button_img.get_rect(center=(SCREEN_WIDTH // 2, create_btn_y))
            create_rect.y += 100
            self.screen.blit(button_img, create_rect)
            if name_text.strip():
                create_color = GRAY if items[active_index] == "create" else BLACK
            else:
                create_color = DISABLED
            create_surf = self.input_font.render("Create", True, create_color)
            self.screen.blit(create_surf, create_surf.get_rect(center=create_rect.center))

            # --- BACK BUTTON ---
            back_rect = button_img.get_rect(center=(SCREEN_WIDTH // 2, back_btn_y))
            back_rect.y += 100
            self.screen.blit(button_img, back_rect)
            back_color = GRAY if items[active_index] == "back" else BLACK
            back_surf = self.input_font.render("Back", True, back_color)
            self.screen.blit(back_surf, back_surf.get_rect(center=back_rect.center))

            pygame.display.flip()
            clock.tick(60)

            # --- Events ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        active_index = (active_index - 1) % len(items)
                    elif event.key == pygame.K_DOWN:
                        active_index = (active_index + 1) % len(items)
                    elif event.key == pygame.K_RETURN:
                        current_item = items[active_index]
                        if current_item == "create" and name_text.strip():
                            self.create_empty_level(name_text, length, height, folder=folder)
                            return
                        elif current_item == "back":
                            return
                    elif event.key == pygame.K_LEFT:
                        if items[active_index] == "length":
                            length = max(length_min, length - 1)
                        elif items[active_index] == "height":
                            height = max(height_min, height - 1)
                    elif event.key == pygame.K_RIGHT:
                        if items[active_index] == "length":
                            length = min(length_max, length + 1)
                        elif items[active_index] == "height":
                            height = min(height_max, height + 1)
                    elif event.key == pygame.K_BACKSPACE:
                        if items[active_index] == "name":
                            name_text = name_text[:-1]
                    else:
                        # Type into name field; limit the name to 10 characters
                        if items[active_index] == "name" and event.unicode.isprintable() and len(name_text) < 10:
                            name_text += event.unicode

    def get_input(self, prompt):
        input_text = ""
        while True:
            self.screen.blit(self.menu_bg, (0, 0))
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
        level[-2][3] = "P"
        level[-2][-3] = "F"
        tiles= {
            "G": "grass",
            "S": "stone",
            ".": "empty",
            "P": "player",
            "C": "collectable",
            "B": "bomber",
            "D": "dirt",
            "H": "heart",
            "E": "pig_enemy",
            "K": "king_pig",
            "F": "finish"
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
            self.screen.blit(self.menu_bg, (0, 0))
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
        options = ["Back"]
        selected = 0
        while True:
            self.screen.blit(self.pause_bg, (0, 0))
            self.draw_menu_buttons(options, selected, start_y=250, spacing=20)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        # Only one option -> no effect
                        pass
                    elif event.key == pygame.K_RETURN:
                        # "Back"
                        return
            self.clock.tick(FPS)

    def lost_menu(self):
        options = ["Restart", "Leave"]
        selected = 0
        while True:
            self.screen.blit(self.pause_bg, (0, 0))
            lost_text = self.font.render("You lost", True, (255, 255, 255))
            self.screen.blit(lost_text, lost_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
            self.draw_menu_buttons(options, selected, start_y=SCREEN_HEIGHT // 2)
            pygame.display.flip()
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        choice = options[selected]
                        if choice == "Restart":
                            self.load_level(self.current_level, folder=self.current_folder)
                            return
                        elif choice == "Leave":
                            return

