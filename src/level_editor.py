# level_editor.py

import pygame
import os
import json

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

LEVELS_FOLDER = "levels"

# ----------------------------------------------------------------
# PALETTES
# ----------------------------------------------------------------

BLOCK_PALETTE = [
    ("G", "assets/images/editor/grass.png"),
    ("S", "assets/images/editor/stone.png"),
    ("D", "assets/images/editor/dirt.png"),
    ("P", "assets/images/editor/player.png"),
    ("X", "assets/images/editor/delete.png"),
]

ENEMY_PALETTE = [
    ("B", "assets/images/editor/bomber.png"),
    ("E", "assets/images/editor/pig.png"),
    ("K", "assets/images/editor/king.png"),
]

COLLECTABLE_PALETTE = [
    ("C", "assets/images/editor/diamond.png"),
    ("H", "assets/images/editor/heart.png"),
]

# Map tile codes -> tile images used for the actual map drawing
TILE_IMAGE_PATHS = {
    ".": None,
    "G": "assets/images/blocks/grass.png",
    "S": "assets/images/blocks/stone.png",
    "D": "assets/images/blocks/dirt.png",
    "P": "assets/images/editor/player.png",
    "B": "assets/images/editor/bomber.png",
    "E": "assets/images/editor/pig.png",
    "K": "assets/images/editor/king.png",
    "C": "assets/images/editor/diamond.png",
    "H": "assets/images/editor/heart.png",
}

def load_level_data(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def save_level_data(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def run_editor(screen, level_name, folder="sandbox"):

    level_path = os.path.join(LEVELS_FOLDER, folder, level_name + ".json")
    level_data = load_level_data(level_path)

    import copy
    original_data = copy.deepcopy(level_data)

    editor = LevelEditor(
        screen=screen,
        level_path=level_path,
        level_data=level_data,
        original_data=original_data
    )
    editor.run()

class LevelEditor:
    def __init__(self, screen, level_path, level_data, original_data):
        self.screen = screen
        self.level_path = level_path
        self.level_data = level_data
        self.original_data = original_data

        self.level_array = self.level_data["level"]
        self.num_rows = len(self.level_array)
        self.num_cols = len(self.level_array[0]) if self.num_rows > 0 else 0

        # Load tile images for map drawing
        self.tile_images = {}
        for code, path in TILE_IMAGE_PATHS.items():
            if path:
                img = pygame.image.load(path).convert_alpha()
                self.tile_images[code] = img
            else:
                self.tile_images[code] = None

        # Load palette icons for the HUD
        self.palette_images = {}
        for (code, path) in BLOCK_PALETTE + ENEMY_PALETTE + COLLECTABLE_PALETTE:
            if code not in self.palette_images:
                self.palette_images[code] = pygame.image.load(path).convert_alpha()

        # Camera offset
        self.camera_x = 0
        self.camera_y = 0

        # possible zoom levels
        self.allowed_zooms = [0.5, 0.75, 1.0, 1.25, 1.5]
        self.zoom_index = 1  # start at 1.0
        self.zoom = self.allowed_zooms[self.zoom_index]

        # Editor UI
        self.show_blocks = False
        self.show_enemies = False
        self.show_collectables = False
        self.selected_tile_code = None

        self.is_placing = False
        self.running = True

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            dt = clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.open_editor_menu()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # wheel up => ZOOM IN
                    mx, my = pygame.mouse.get_pos()
                    self.zoom_in(mx, my)
                elif event.button == 5:  # wheel down => ZOOM OUT
                    mx, my = pygame.mouse.get_pos()
                    self.zoom_out(mx, my)

                elif event.button == 1:  # left click
                    mx, my = pygame.mouse.get_pos()
                    if self.click_hud(mx, my):
                        pass
                    else:
                        self.is_placing = True
                        self.place_tile(mx, my)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_placing = False

            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[2]:  # right button drag => pan camera
                    rel = event.rel
                    self.camera_x -= rel[0]
                    self.camera_y -= rel[1]

                if self.is_placing and pygame.mouse.get_pressed()[0]:
                    mx, my = pygame.mouse.get_pos()
                    self.place_tile(mx, my)

    def zoom_in(self, mx, my):
        """Zoom in pivoting around mouse (mx, my)."""
        if self.zoom_index < len(self.allowed_zooms) - 1:
            old_zoom = self.zoom
            old_world_x = (mx + self.camera_x) / old_zoom
            old_world_y = (my + self.camera_y) / old_zoom

            self.zoom_index += 1
            self.zoom = self.allowed_zooms[self.zoom_index]

            # Adjust camera so that (mx,my) stays at same world coord
            new_world_x = old_world_x * self.zoom
            new_world_y = old_world_y * self.zoom
            self.camera_x = new_world_x - mx
            self.camera_y = new_world_y - my

    def zoom_out(self, mx, my):
        """Zoom out pivoting around mouse (mx, my)."""
        if self.zoom_index > 0:
            old_zoom = self.zoom
            old_world_x = (mx + self.camera_x) / old_zoom
            old_world_y = (my + self.camera_y) / old_zoom

            self.zoom_index -= 1
            self.zoom = self.allowed_zooms[self.zoom_index]

            new_world_x = old_world_x * self.zoom
            new_world_y = old_world_y * self.zoom
            self.camera_x = new_world_x - mx
            self.camera_y = new_world_y - my

    def open_editor_menu(self):
        menu_open = True
        options = ["Resume", "Undo changes", "Save and exit"]
        current_choice = 0

        font = pygame.font.SysFont(None, 50)

        while menu_open:
            self.screen.fill((50, 50, 50))
            y_start = 300
            for i, opt in enumerate(options):
                color = (255, 255, 0) if i == current_choice else (200, 200, 200)
                surf = font.render(opt, True, color)
                rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y_start))
                self.screen.blit(surf, rect)
                y_start += 60

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_open = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        current_choice = max(0, current_choice - 1)
                    elif event.key == pygame.K_DOWN:
                        current_choice = min(len(options) - 1, current_choice + 1)
                    elif event.key == pygame.K_RETURN:
                        chosen = options[current_choice]
                        if chosen == "Resume":
                            menu_open = False
                        elif chosen == "Undo changes":
                            import copy
                            self.level_data = copy.deepcopy(self.original_data)
                            self.level_array = self.level_data["level"]
                            self.num_rows = len(self.level_array)
                            self.num_cols = len(self.level_array[0]) if self.num_rows > 0 else 0
                            menu_open = False
                        elif chosen == "Save and exit":
                            self.save_level()
                            menu_open = False
                            self.running = False
                    elif event.key == pygame.K_ESCAPE:
                        menu_open = False

    def update(self):
        # clamp camera so we don't see outside map
        display_tile_size = TILE_SIZE * self.zoom
        map_pix_w = self.num_cols * display_tile_size
        map_pix_h = self.num_rows * display_tile_size

        if map_pix_w < SCREEN_WIDTH:
            self.camera_x = 0
        else:
            max_x = map_pix_w - SCREEN_WIDTH
            if self.camera_x < 0:
                self.camera_x = 0
            elif self.camera_x > max_x:
                self.camera_x = max_x

        if map_pix_h < SCREEN_HEIGHT:
            self.camera_y = 0
        else:
            max_y = map_pix_h - SCREEN_HEIGHT
            if self.camera_y < 0:
                self.camera_y = 0
            elif self.camera_y > max_y:
                self.camera_y = max_y

    def draw(self):
        self.screen.fill((100, 200, 250))
        self.draw_level()
        self.draw_grid()
        self.draw_hud()

    def draw_level(self):
        display_tile_size = int(TILE_SIZE * self.zoom)

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                tile_code = self.level_array[row][col]
                if tile_code == ".":
                    continue
                tile_img = self.tile_images.get(tile_code)
                if not tile_img:
                    continue

                screen_x = int(col * display_tile_size - self.camera_x)
                screen_y = int(row * display_tile_size - self.camera_y)

                scaled_img = pygame.transform.scale(tile_img, (display_tile_size, display_tile_size))
                self.screen.blit(scaled_img, (screen_x, screen_y))

    def draw_grid(self):
        display_tile_size = int(TILE_SIZE * self.zoom)
        grid_color = (200, 200, 200)

        for r in range(self.num_rows + 1):
            y = r * display_tile_size - self.camera_y
            pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y), 1)

        for c in range(self.num_cols + 1):
            x = c * display_tile_size - self.camera_x
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)

    def draw_hud(self):
        top_bar_height = 50
        pygame.draw.rect(self.screen, (50, 50, 50), (0, 0, SCREEN_WIDTH, top_bar_height))

        blocks_btn_rect = pygame.Rect(10, 10, 100, 30)
        enemies_btn_rect = pygame.Rect(120, 10, 100, 30)
        collect_btn_rect = pygame.Rect(230, 10, 120, 30)

        # 1) Highlight the active category in a lighter color
        if self.show_blocks:
            pygame.draw.rect(self.screen, (160, 160, 160), blocks_btn_rect)
        else:
            pygame.draw.rect(self.screen, (100, 100, 100), blocks_btn_rect)

        if self.show_enemies:
            pygame.draw.rect(self.screen, (160, 160, 160), enemies_btn_rect)
        else:
            pygame.draw.rect(self.screen, (100, 100, 100), enemies_btn_rect)

        if self.show_collectables:
            pygame.draw.rect(self.screen, (160, 160, 160), collect_btn_rect)
        else:
            pygame.draw.rect(self.screen, (100, 100, 100), collect_btn_rect)

        font = pygame.font.SysFont(None, 30)
        self.screen.blit(font.render("Blocks", True, (255, 255, 255)), (blocks_btn_rect.x + 10, blocks_btn_rect.y + 5))
        self.screen.blit(font.render("Enemies", True, (255, 255, 255)), (enemies_btn_rect.x + 10, enemies_btn_rect.y + 5))
        self.screen.blit(font.render("Collect.", True, (255, 255, 255)), (collect_btn_rect.x + 10, collect_btn_rect.y + 5))

        if self.show_blocks:
            self.draw_palette(BLOCK_PALETTE)
        elif self.show_enemies:
            self.draw_palette(ENEMY_PALETTE)
        elif self.show_collectables:
            self.draw_palette(COLLECTABLE_PALETTE)

    def draw_palette(self, palette_items):
        bottom_bar_height = 100
        y = SCREEN_HEIGHT - bottom_bar_height
        pygame.draw.rect(self.screen, (80, 80, 80), (0, y, SCREEN_WIDTH, bottom_bar_height))

        x_offset = 50
        for (code, path) in palette_items:
            rect = pygame.Rect(x_offset, y + 20, 60, 60)

            # If this item is the selected tile, highlight the background
            if code == self.selected_tile_code:
                pygame.draw.rect(self.screen, (180, 180, 180), rect)
            else:
                pygame.draw.rect(self.screen, (150, 150, 150), rect)

            icon = self.palette_images.get(code, None)
            if icon:
                icon_surf = pygame.transform.scale(icon, (60, 60))
                self.screen.blit(icon_surf, rect.topleft)

            x_offset += 70

    def click_hud(self, mx, my):
        blocks_btn_rect = pygame.Rect(10, 10, 100, 30)
        enemies_btn_rect = pygame.Rect(120, 10, 100, 30)
        collect_btn_rect = pygame.Rect(230, 10, 120, 30)

        if blocks_btn_rect.collidepoint(mx, my):
            self.show_blocks = not self.show_blocks
            self.show_enemies = False
            self.show_collectables = False
            return True
        if enemies_btn_rect.collidepoint(mx, my):
            self.show_enemies = not self.show_enemies
            self.show_blocks = False
            self.show_collectables = False
            return True
        if collect_btn_rect.collidepoint(mx, my):
            self.show_collectables = not self.show_collectables
            self.show_blocks = False
            self.show_enemies = False
            return True

        bottom_bar_height = 100
        palette_y = SCREEN_HEIGHT - bottom_bar_height
        if my >= palette_y:
            if self.show_blocks:
                self.detect_palette_click(mx, my, BLOCK_PALETTE)
            elif self.show_enemies:
                self.detect_palette_click(mx, my, ENEMY_PALETTE)
            elif self.show_collectables:
                self.detect_palette_click(mx, my, COLLECTABLE_PALETTE)
            return True

        return False

    def detect_palette_click(self, mx, my, palette_items):
        bottom_bar_height = 100
        y = SCREEN_HEIGHT - bottom_bar_height
        x_offset = 50

        for (code, path) in palette_items:
            rect = pygame.Rect(x_offset, y + 20, 60, 60)
            if rect.collidepoint(mx, my):
                self.selected_tile_code = code
                return
            x_offset += 70

    def place_tile(self, mx, my):
        if not self.selected_tile_code:
            return

        # Convert screen coords -> world coords
        world_x = (mx + self.camera_x) / self.zoom
        world_y = (my + self.camera_y) / self.zoom

        col = int(world_x // TILE_SIZE)
        row = int(world_y // TILE_SIZE)

        # Prevent placing on the border
        if row == 0 or row == self.num_rows - 1 or col == 0 or col == self.num_cols - 1:
            return

        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            if self.selected_tile_code == "X":
                self.level_array[row][col] = "."
            elif self.selected_tile_code == "P":
                self.remove_existing_player()
                self.level_array[row][col] = "P"
            else:
                self.level_array[row][col] = self.selected_tile_code

    def remove_existing_player(self):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.level_array[r][c] == "P":
                    self.level_array[r][c] = "."

    def save_level(self):
        self.level_data["level"] = self.level_array
        save_level_data(self.level_path, self.level_data)
