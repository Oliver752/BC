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
        self.folder_btn_img = pygame.image.load("assets/images/btn/folder.png").convert_alpha()
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
        self.title_bg_img = pygame.image.load("assets/images/btn/titlebg.png").convert_alpha()

        # Diamond count resets each level
        self.diamond_count = 0

        # Track current level/folder so we can restart
        self.current_level = None
        self.current_folder = None

        # Load menu sound assets
        self.menu_select = pygame.mixer.Sound("assets/sounds/other/selection.wav")
        self.menu_click = pygame.mixer.Sound("assets/sounds/other/click.flac")

    def draw_title_with_bg(self, text, center_y=120):
        # Draw the background image
        title_rect = self.title_bg_img.get_rect(center=(SCREEN_WIDTH // 2, center_y))
        self.screen.blit(self.title_bg_img, title_rect)

        # Draw the text on top of the background
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=title_rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_menu_buttons(self, options, selected_index, start_y=200, spacing=80):
        """
        Draws each option as a button image with text on top, stacked vertically.
        :options: list of strings
        :selected_index: which option is highlighted
        :start_y: vertical start position
        :spacing: vertical space between buttons
        """
        for i, text in enumerate(options):
            x = SCREEN_WIDTH // 2 - self.button_width // 2
            y = start_y + i * (self.button_height + spacing)
            rect = pygame.Rect(x, y, self.button_width, self.button_height)
            self.screen.blit(self.button_img, rect)
            color = (128, 128, 128) if i == selected_index else (0, 0, 0)
            surf = self.font.render(text, True, color)
            surf_rect = surf.get_rect(center=rect.center)
            self.screen.blit(surf, surf_rect)

    def display_message(self, message, duration=2):
        """Helper to display a temporary message on screen."""
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < duration * 1000:
            self.screen.fill((0, 0, 0))
            text = self.font.render(message, True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            pygame.display.flip()
            self.clock.tick(30)

    def get_input(self, prompt):
        """
        Displays a prompt and a text field (from field.png).
        The user types in the field (up to 8 characters) and presses Enter to confirm.
        """
        import sys
        input_text = ""

        # Load your field image with alpha
        field_img = pygame.image.load("assets/images/btn/field.png").convert_alpha()

        while True:
            # Draw background
            self.screen.blit(self.menu_bg, (0, 0))

            # Draw the prompt above the field
            self.draw_title_with_bg(prompt, center_y=440)


            # Draw the field image first
            field_rect = field_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(field_img, field_rect)

            # Then draw the typed text on top of the field
            text_surf = self.input_font.render(input_text, True, (0, 0, 0))  # black text
            text_rect = text_surf.get_rect(center=field_rect.center)
            self.screen.blit(text_surf, text_rect)

            pygame.display.flip()
            self.clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return input_text  # Done typing
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        # If you want ESC to just cancel and return an empty string:
                        return ""
                    else:
                        # If printable and we haven't reached 8 chars, append
                        if event.unicode.isprintable() and len(input_text) < 8:
                            input_text += event.unicode

    def confirm_action(self, prompt):
        """
        Displays a confirmation prompt with a yes/no dialog.
        Returns True if user selects "Yes", otherwise False.
        """
        yes_no_options = ["Yes", "No"]
        selected = 0

        while True:
            self.screen.blit(self.pause_bg, (0, 0))

            title_rect = self.title_bg_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(self.title_bg_img, title_rect)

            text_surf = self.font.render(prompt, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=title_rect.center)
            self.screen.blit(text_surf, text_rect)

            start_y = SCREEN_HEIGHT // 2
            self.draw_menu_buttons(yes_no_options, selected, start_y=start_y, spacing=20)

            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(yes_no_options)
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(yes_no_options)
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_RETURN:
                        self.menu_click.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_click.play()
                        return (yes_no_options[selected] == "Yes")
                    elif event.key == pygame.K_ESCAPE:

                        return False

    def main_menu(self):
        pygame.mixer.music.stop()  # Stop any previous music
        pygame.mixer.music.load("assets/sounds/music/menu_music.wav")
        pygame.mixer.music.set_volume(MUSIC_VOLUME / 10.0)
        pygame.mixer.music.play(-1)  # Loop indefinitely
        options = ["Play", "Sandbox", "Settings", "Quit"]
        selected = 0
        while True:
            self.screen.blit(self.menu_bg, (0, 0))
            title_rect = self.title_img.get_rect(midtop=(SCREEN_WIDTH // 2, 130))
            self.screen.blit(self.title_img, title_rect)
            self.draw_menu_buttons(options, selected, start_y=300, spacing=20)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_RETURN:
                        self.menu_click.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_click.play()
                        choice = options[selected]
                        if choice == "Play":
                            self.level_select(folder="default")
                        elif choice == "Sandbox":
                            self.sandbox_folder_menu()
                        elif choice == "Settings":
                            self.settings_menu()
                        elif choice == "Quit":
                            pygame.quit()
                            sys.exit()
            self.clock.tick(FPS)

    def level_select(self, folder="default"):
        folder_path = os.path.join("levels", folder)
        all_files = os.listdir(folder_path)
        levels = [f[:-5] for f in all_files if f.endswith(".json")]
        levels.append("Back")
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
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(levels)
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_RETURN:
                        self.menu_click.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_click.play()
                        choice = levels[selected]
                        if choice == "Back":
                            return
                        else:
                            self.load_level(choice + ".json", folder=folder)
                            return
            self.clock.tick(FPS)

    def sandbox_folder_menu(self):
        """Folder selection for sandbox levels in a 2x2 (or more) grid with vertically stacked bottom buttons."""
        base_folder = os.path.join("levels", "sandbox")
        os.makedirs(base_folder, exist_ok=True)
        # Ensure the folder button image is loaded
        if not hasattr(self, "folder_btn_img"):
            self.folder_btn_img = pygame.image.load("assets/images/btn/folder.png").convert_alpha()

        while True:
            # Get only directories inside levels/sandbox.
            folders = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))]
            grid_count = len(folders)

            # Decide which bottom buttons to show:
            # Hide "Create New Folder" if we have >= 6 folders.
            if grid_count < 6:
                bottom_options = ["Add Folder", "Back"]
            else:
                bottom_options = ["Back"]

            # Initial selection state:
            # If there are folders, start in the grid zone; otherwise start at the bottom zone.
            active_zone = "grid" if grid_count > 0 else "bottom"
            selected_grid_index = 0
            selected_bottom_index = 0

            # Because bottom_options can have 1 or 2 items, ensure we don't pick an out-of-range index.
            bottom_options_count = len(bottom_options)
            if selected_bottom_index >= bottom_options_count:
                selected_bottom_index = bottom_options_count - 1

            while True:
                self.screen.blit(self.menu_bg, (0, 0))
                # Draw title
                self.draw_title_with_bg("Sandbox Folders", center_y=120)
                # --- Draw Folder Grid ---
                if grid_count > 0:
                    spacing_x = 100
                    spacing_y = 40
                    folder_width = 200  # folder.png is 200×160
                    folder_height = 160
                    grid_total_width = 2 * folder_width + spacing_x
                    grid_left = (SCREEN_WIDTH - grid_total_width) // 2
                    grid_top = 200

                    for i, folder_name in enumerate(folders):
                        row = i // 2
                        col = i % 2
                        x = grid_left + col * (folder_width + spacing_x)
                        y = grid_top + row * (folder_height + spacing_y)
                        rect = pygame.Rect(x, y, folder_width, folder_height)
                        self.screen.blit(self.folder_btn_img, rect)
                        self.folder_font = pygame.font.Font(None, 30)
                        # Highlight if this folder is selected
                        if active_zone == "grid" and selected_grid_index == i:
                            text_color = (128, 128, 128)
                        else:
                            text_color = (0, 0, 0)
                        folder_text = self.folder_font.render(folder_name, True, text_color)
                        text_rect = folder_text.get_rect(center=rect.center)
                        text_rect.x -= 20
                        text_rect.y -= 20
                        self.screen.blit(folder_text, text_rect)

                # --- Draw Bottom Buttons (Vertical Stack) ---
                bottom_margin = 50
                spacing = 20
                btn_w = self.button_width  # your standard button image width
                btn_h = self.button_height  # your standard button image height
                total_bottom_height = bottom_options_count * btn_h + (bottom_options_count - 1) * spacing
                bottom_top = SCREEN_HEIGHT - bottom_margin - total_bottom_height

                for j, option in enumerate(bottom_options):
                    x = (SCREEN_WIDTH - btn_w) // 2
                    y = bottom_top + j * (btn_h + spacing)
                    rect = pygame.Rect(x, y, btn_w, btn_h)
                    self.screen.blit(self.button_img, rect)

                    # Highlight if selected
                    if active_zone == "bottom" and selected_bottom_index == j:
                        text_color = (128, 128, 128)
                    else:
                        text_color = (0, 0, 0)

                    text_surf = self.font.render(option, True, text_color)
                    text_rect = text_surf.get_rect(center=rect.center)
                    self.screen.blit(text_surf, text_rect)

                pygame.display.flip()

                # --- Event Handling ---
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                            # Always play selection sound when navigating
                            self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                            self.menu_select.play()

                        if event.key == pygame.K_LEFT:
                            if active_zone == "grid":
                                # Move left in the grid if possible
                                if selected_grid_index % 2 > 0:
                                    selected_grid_index -= 1

                        elif event.key == pygame.K_RIGHT:
                            if active_zone == "grid":
                                # Move right in the grid if possible
                                if (selected_grid_index % 2) < 1 and selected_grid_index < grid_count - 1:
                                    selected_grid_index += 1

                        elif event.key == pygame.K_UP:
                            if active_zone == "bottom":
                                # Move up within bottom options if possible
                                if selected_bottom_index > 0:
                                    selected_bottom_index -= 1
                                else:
                                    # If we're at the top of the bottom list, move to grid if folders exist
                                    if grid_count > 0:
                                        active_zone = "grid"
                            elif active_zone == "grid":
                                # Move up in the grid if possible
                                if selected_grid_index >= 2:
                                    selected_grid_index -= 2

                        elif event.key == pygame.K_DOWN:
                            if active_zone == "grid":
                                # Move down in the grid or switch to bottom zone
                                current_row = selected_grid_index // 2
                                total_rows = (grid_count + 1) // 2  # number of rows
                                if current_row == total_rows - 1:
                                    # On the last row -> move to bottom zone
                                    active_zone = "bottom"
                                else:
                                    selected_grid_index += 2
                            elif active_zone == "bottom":
                                # Move down in bottom options if possible
                                if selected_bottom_index < bottom_options_count - 1:
                                    selected_bottom_index += 1

                        elif event.key == pygame.K_RETURN:
                            self.menu_click.set_volume(EFFECTS_VOLUME / 10.0)
                            self.menu_click.play()
                            if active_zone == "grid":
                                folder_choice = folders[selected_grid_index]
                                self.sandbox_folder_actions(folder_choice)
                                break  # Refresh folder list
                            else:  # active_zone == "bottom"
                                choice = bottom_options[selected_bottom_index]
                                if choice == "Add Folder":
                                    self.create_new_folder()
                                    break  # Refresh folder list
                                elif choice == "Back":
                                    return

                else:
                    # If we didn't break, keep going
                    continue

                # If we broke out of the loop, refresh folder list
                break

    def create_new_folder(self):
        """Prompt user for a new folder name and create it under levels/sandbox."""
        folder_name = self.get_input("Enter new folder name:")
        if folder_name.strip():
            new_folder_path = os.path.join("levels", "sandbox", folder_name)
            if os.path.exists(new_folder_path):
                self.display_message("Folder already exists!")
            else:
                os.makedirs(new_folder_path)
                self.display_message(f"Folder '{folder_name}' created.")
        else:
            self.display_message("Invalid name!")

    def sandbox_folder_actions(self, folder_name):
        """
        Present a submenu for a selected sandbox folder.
        Options: Create Level, Browse Levels, (optionally Delete Folder if empty), Back.
        """
        folder_path = os.path.join("levels", "sandbox", folder_name)
        while True:
            # Check for existing level files (.json) in this folder
            levels_in_folder = [f for f in os.listdir(folder_path) if f.endswith(".json")]
            options = ["Create Level", "Browse Levels"]
            if not levels_in_folder:
                options.append("Delete Folder")
            options.append("Back")
            selected = 0
            while True:
                self.screen.blit(self.menu_bg, (0, 0))
                self.draw_title_with_bg(f"Folder: {folder_name}", center_y=120)

                self.draw_menu_buttons(options, selected, start_y=250, spacing=20)
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            selected = (selected - 1) % len(options)
                            self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                            self.menu_select.play()
                        elif event.key == pygame.K_DOWN:
                            selected = (selected + 1) % len(options)
                            self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                            self.menu_select.play()
                        elif event.key == pygame.K_RETURN:
                            self.menu_click.set_volume(EFFECTS_VOLUME / 10.0)
                            self.menu_click.play()
                            choice = options[selected]
                            if choice == "Back":
                                return
                            elif choice == "Create Level":
                                # Ensure folder has less than 5 levels
                                if len(levels_in_folder) >= 5:
                                    self.display_message("Max 5 levels reached in this folder!")
                                    break
                                self.create_new_level(folder=os.path.join("sandbox", folder_name))
                                break
                            elif choice == "Browse Levels":
                                self.sandbox_browse_levels(folder=os.path.join("sandbox", folder_name))
                                break
                            elif choice == "Delete Folder":
                                if self.confirm_action("Delete this folder?"):
                                    os.rmdir(folder_path)
                                    self.display_message("Folder deleted.")
                                    return
                                else:
                                    self.display_message("Folder deletion cancelled.")
                                    break
                else:
                    continue
                break

    def create_new_level(self, folder="default"):
        """
        Opens the level creation screen.
        In sandbox folders, folder should be like "sandbox/FolderName".
        """

        full_folder = os.path.join("levels", folder)
        levels_in_folder = [f for f in os.listdir(full_folder) if f.endswith(".json")]

        pygame.key.set_repeat(200, 40)

        button_img = pygame.image.load("assets/images/btn/button.png").convert_alpha()
        field_img = pygame.image.load("assets/images/btn/field.png").convert_alpha()
        arrow_left_img = pygame.image.load("assets/images/btn/arrow_left.png").convert_alpha()
        arrow_right_img = pygame.image.load("assets/images/btn/arrow_right.png").convert_alpha()

        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GRAY = (128, 128, 128)
        DISABLED = (70, 70, 70)

        length_min, length_max = 30, 100
        height_min, height_max = 20, 50

        length = length_min
        height = height_min
        name_text = ""

        items = ["length", "height", "name", "create", "back"]
        active_index = 0

        title_y = 80
        length_label_y = 240
        length_row_y = 280
        height_label_y = 370
        height_row_y = 320
        name_label_y = 510
        name_field_y = 480
        create_btn_y = 600
        back_btn_y = 700
        ARROW_OFFSET = 80

        clock = pygame.time.Clock()

        while True:
            self.screen.blit(self.pause_bg, (0, 0))

            title_surf = self.font.render("Create New Level", True, WHITE)
            self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, title_y)))

            # LENGTH
            length_label_color = GRAY if items[active_index] == "length" else WHITE
            length_label_surf = self.input_font.render("Length", True, length_label_color)
            self.screen.blit(length_label_surf, length_label_surf.get_rect(center=(SCREEN_WIDTH // 2, length_label_y)))
            left_rect_len = arrow_left_img.get_rect(midright=(SCREEN_WIDTH // 2 - ARROW_OFFSET, length_row_y))
            right_rect_len = arrow_right_img.get_rect(midleft=(SCREEN_WIDTH // 2 + ARROW_OFFSET, length_row_y))
            length_val_color = GRAY if items[active_index] == "length" else BLACK
            length_val_surf = self.input_font.render(str(length), True, length_val_color)
            length_val_rect = length_val_surf.get_rect(center=(SCREEN_WIDTH // 2, length_row_y))
            self.screen.blit(arrow_left_img, left_rect_len)
            self.screen.blit(length_val_surf, length_val_rect)
            self.screen.blit(arrow_right_img, right_rect_len)

            # HEIGHT
            height_label_color = GRAY if items[active_index] == "height" else WHITE
            height_label_surf = self.input_font.render("Height", True, height_label_color)
            self.screen.blit(height_label_surf, height_label_surf.get_rect(center=(SCREEN_WIDTH // 2, height_label_y)))
            left_rect_h = arrow_left_img.get_rect(midright=(SCREEN_WIDTH // 2 - ARROW_OFFSET, height_row_y + 100))
            right_rect_h = arrow_right_img.get_rect(midleft=(SCREEN_WIDTH // 2 + ARROW_OFFSET, height_row_y + 100))
            height_val_color = GRAY if items[active_index] == "height" else BLACK
            height_val_surf = self.input_font.render(str(height), True, height_val_color)
            height_val_rect = height_val_surf.get_rect(center=(SCREEN_WIDTH // 2, height_row_y + 100))
            self.screen.blit(arrow_left_img, left_rect_h)
            self.screen.blit(height_val_surf, height_val_rect)
            self.screen.blit(arrow_right_img, right_rect_h)

            # NAME
            name_label_color = GRAY if items[active_index] == "name" else WHITE
            name_label_surf = self.input_font.render("Name", True, name_label_color)
            self.screen.blit(name_label_surf, name_label_surf.get_rect(center=(SCREEN_WIDTH // 2, name_label_y)))
            field_rect = field_img.get_rect(center=(SCREEN_WIDTH // 2, name_field_y + 100))
            self.screen.blit(field_img, field_rect)
            name_color = GRAY if items[active_index] == "name" else BLACK
            name_surf = self.input_font.render(name_text, True, name_color)
            name_surf_rect = name_surf.get_rect(center=field_rect.center)
            self.screen.blit(name_surf, name_surf_rect)

            # CREATE BUTTON
            create_rect = button_img.get_rect(center=(SCREEN_WIDTH // 2, create_btn_y + 100))
            self.screen.blit(button_img, create_rect)
            create_color = GRAY if items[active_index] == "create" else (BLACK if name_text.strip() else DISABLED)
            create_surf = self.input_font.render("Create", True, create_color)
            self.screen.blit(create_surf, create_surf.get_rect(center=create_rect.center))

            # BACK BUTTON
            back_rect = button_img.get_rect(center=(SCREEN_WIDTH // 2, back_btn_y + 100))
            self.screen.blit(button_img, back_rect)
            back_color = GRAY if items[active_index] == "back" else BLACK
            back_surf = self.input_font.render("Back", True, back_color)
            self.screen.blit(back_surf, back_surf.get_rect(center=back_rect.center))

            pygame.display.flip()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        active_index = (active_index - 1) % len(items)
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_DOWN:
                        active_index = (active_index + 1) % len(items)
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_RETURN:
                        self.menu_click.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_click.play()
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
                        if items[active_index] == "name" and event.unicode.isprintable() and len(name_text) < 10:
                            name_text += event.unicode

    def create_empty_level(self, name, width, height, folder="default"):
        level = [["." for _ in range(width)] for _ in range(height)]
        level[0] = ["G"] * width
        level[-1] = ["S"] * width
        for row in level:
            row[0] = "G"
            row[-1] = "G"
        level[-2][3] = "P"
        level[-2][-3] = "F"
        tiles = {
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
        os.makedirs(f'levels/{folder}', exist_ok=True)
        with open(f"levels/{folder}/{name}.json", 'w') as file:
            json.dump({"level": level, "tiles": tiles}, file, indent=4)
        print(f"Level {name} created in levels/{folder}.")

    def sandbox_browse_levels(self, folder):
        while True:

            folder_path = os.path.join("levels", folder)
            levels = [f[:-5] for f in os.listdir(folder_path) if f.endswith(".json")]
            levels.append("Back")
            selected = 0

            while True:
                self.screen.blit(self.pause_bg, (0, 0))
                self.draw_menu_buttons(levels, selected, start_y=200, spacing=20)
                pygame.display.flip()
                self.clock.tick(FPS)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            selected = (selected - 1) % len(levels)
                            self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                            self.menu_select.play()
                        elif event.key == pygame.K_DOWN:
                            selected = (selected + 1) % len(levels)
                            self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                            self.menu_select.play()
                        elif event.key == pygame.K_RETURN:
                            self.menu_click.set_volume(EFFECTS_VOLUME / 10.0)
                            self.menu_click.play()
                            choice = levels[selected]
                            if choice == "Back":
                                return
                            else:
                                self.sandbox_level_sub_menu(choice, folder)
                                # After sub-menu returns, break to refresh the levels list
                                break
                        elif event.key == pygame.K_ESCAPE:
                            return
                else:
                    # If we never broke, continue
                    continue
                # Re-check the folder contents
                break
            # Refresh the list

    def sandbox_level_sub_menu(self, level_name, folder):
        """Submenu for a specific level with options: Play, Edit, Delete, Back."""
        options = ["Play", "Edit", "Delete", "Back"]
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
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()

                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()

                    elif event.key == pygame.K_RETURN:
                        self.menu_click.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_click.play()

                        choice = options[selected]
                        if choice == "Back":
                            # Return to the parent menu without doing anything
                            return

                        elif choice == "Play":
                            self.load_level(level_name + ".json", folder=folder)
                            return  # After loading, go back to the parent menu

                        elif choice == "Edit":
                            run_editor(self.screen, level_name, folder)
                            return  # After editing refresh

                        elif choice == "Delete":
                            if self.confirm_action("Delete this level?"):
                                level_path = os.path.join("levels", folder, level_name + ".json")
                                if os.path.exists(level_path):
                                    os.remove(level_path)
                                    self.display_message("Level deleted.")
                                else:
                                    self.display_message("File not found.")
                            else:
                                self.display_message("Deletion cancelled.")

                            # return to refresh its list
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
        self.run_level(all_sprites, player, blocks, collectables, enemies, door_group)

    def run_level(self, all_sprites, player, blocks, collectables, enemies, door_group):
        bombs = pygame.sprite.Group()
        running = True
        pygame.mixer.music.stop()
        pygame.mixer.music.load("assets/sounds/music/game_music.wav")
        pygame.mixer.music.set_volume(MUSIC_VOLUME / 10.0)
        pygame.mixer.music.play(-1)

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
                            self.switch_to_menu_music()
                            return

            player.update(blocks, bombs, enemies)
            collectables.update()
            bombs.update(blocks, player)
            for enemy in enemies:
                if hasattr(enemy, 'throw_bomb'):
                    enemy.update(player, blocks, bombs)
                else:
                    enemy.update(player, blocks)

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

            for door in door_group:
                door.update(self.diamond_count, player, keys)

            self.camera.update(player)
            self.screen.blit(self.game_bg, (0, 0))
            for door in door_group:
                door.draw_image(self.screen, self.camera)
            for sprite in all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
            for bomb in bombs:
                self.screen.blit(bomb.image, self.camera.apply(bomb))
            for door in door_group:
                door.draw_ui(self.screen, self.font, self.diamond_count, self.camera)

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
            self.screen.blit(self.pause_bg, (0, 0))
            self.draw_title_with_bg("Paused", center_y=100)

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
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_RETURN:
                        self.menu_click.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_click.play()
                        return options[selected].lower()
                    elif event.key == pygame.K_ESCAPE:
                        self.switch_to_menu_music()
                        return "resume"

    def settings_menu(self):
        import settings

        # Enable key repeat
        pygame.key.set_repeat(200, 140)


        field_img = pygame.image.load("assets/images/btn/field.png").convert_alpha()
        arrow_left_img = pygame.image.load("assets/images/btn/arrow_left.png").convert_alpha()
        arrow_right_img = pygame.image.load("assets/images/btn/arrow_right.png").convert_alpha()

        effects = settings.EFFECTS_VOLUME
        music = settings.MUSIC_VOLUME


        options = ["Effects", "Music", "Back"]
        selected = 0

        running = True
        while running:
            self.screen.blit(self.menu_bg, (0, 0))

            # --- Title ---
            self.draw_title_with_bg("Volume Settings", center_y=150)
            # --- Effects Section ---
            effects_label_color = (128, 128, 128) if selected == 0 else (0, 0, 0)
            effects_label = self.input_font.render("Effects", True, effects_label_color)
            effects_label_rect = effects_label.get_rect(center=(SCREEN_WIDTH // 2, 250))
            self.screen.blit(effects_label, effects_label_rect)

            effects_field_rect = field_img.get_rect(center=(SCREEN_WIDTH // 2, 320))
            self.screen.blit(field_img, effects_field_rect)
            left_arrow_rect = arrow_left_img.get_rect(
                midright=(effects_field_rect.left - 10, effects_field_rect.centery))
            right_arrow_rect = arrow_right_img.get_rect(
                midleft=(effects_field_rect.right + 10, effects_field_rect.centery))
            self.screen.blit(arrow_left_img, left_arrow_rect)
            self.screen.blit(arrow_right_img, right_arrow_rect)
            effects_value_color = (128, 128, 128) if selected == 0 else (0, 0, 0)
            effects_value_text = self.input_font.render(str(effects), True, effects_value_color)
            effects_value_rect = effects_value_text.get_rect(center=effects_field_rect.center)
            self.screen.blit(effects_value_text, effects_value_rect)

            # --- Music Section ---
            music_label_color = (128, 128, 128) if selected == 1 else (0, 0, 0)
            music_label = self.input_font.render("Music", True, music_label_color)
            music_label_rect = music_label.get_rect(center=(SCREEN_WIDTH // 2, 400))
            self.screen.blit(music_label, music_label_rect)

            music_field_rect = field_img.get_rect(center=(SCREEN_WIDTH // 2, 470))
            self.screen.blit(field_img, music_field_rect)
            left_arrow_rect2 = arrow_left_img.get_rect(midright=(music_field_rect.left - 10, music_field_rect.centery))
            right_arrow_rect2 = arrow_right_img.get_rect(
                midleft=(music_field_rect.right + 10, music_field_rect.centery))
            self.screen.blit(arrow_left_img, left_arrow_rect2)
            self.screen.blit(arrow_right_img, right_arrow_rect2)
            music_value_color = (128, 128, 128) if selected == 1 else (0, 0, 0)
            music_value_text = self.input_font.render(str(music), True, music_value_color)
            music_value_rect = music_value_text.get_rect(center=music_field_rect.center)
            self.screen.blit(music_value_text, music_value_rect)

            # --- Back Button ---
            back_color = (128, 128, 128) if selected == 2 else (0, 0, 0)
            back_rect = self.button_img.get_rect(center=(SCREEN_WIDTH // 2, 600))
            self.screen.blit(self.button_img, back_rect)
            back_text = self.font.render("Back", True, back_color)
            back_text_rect = back_text.get_rect(center=back_rect.center)
            self.screen.blit(back_text, back_text_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                        self.menu_select.set_volume(settings.EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                        self.menu_select.set_volume(settings.EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_LEFT:
                        if selected == 0:
                            effects = max(0, effects - 1)
                        elif selected == 1:
                            music = max(0, music - 1)
                    elif event.key == pygame.K_RIGHT:
                        if selected == 0:
                            effects = min(10, effects + 1)
                        elif selected == 1:
                            music = min(10, music + 1)
                    elif event.key == pygame.K_RETURN:
                        self.menu_click.set_volume(settings.EFFECTS_VOLUME / 10.0)
                        self.menu_click.play()
                        if options[selected] == "Back":

                            settings.EFFECTS_VOLUME = effects
                            settings.MUSIC_VOLUME = music
                            new_effects_vol = effects / 10.0
                            new_music_vol = music / 15.0

                            self.menu_select.set_volume(new_effects_vol)
                            self.menu_click.set_volume(new_effects_vol)
                            pygame.mixer.music.set_volume(new_music_vol)  # refresh music volume
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
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
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_RETURN:
                        self.menu_click.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_click.play()
                        choice = options[selected]
                        if choice == "Continue":
                            self.level_select(folder=self.current_folder)
                            return
                        elif choice == "Leave":
                            self.switch_to_menu_music()
                            return

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
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                        self.menu_select.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_select.play()
                    elif event.key == pygame.K_RETURN:
                        self.menu_click.set_volume(EFFECTS_VOLUME / 10.0)
                        self.menu_click.play()
                        choice = options[selected]
                        if choice == "Restart":
                            self.load_level(self.current_level, folder=self.current_folder)
                            return
                        elif choice == "Leave":
                            self.switch_to_menu_music()
                            return

    def switch_to_menu_music(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.load("assets/sounds/music/menu_music.wav")
        pygame.mixer.music.set_volume(MUSIC_VOLUME / 10.0)
        pygame.mixer.music.play(-1)



