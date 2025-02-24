import pygame
import sys
import json
import os
from settings import *
from blocks import Block
from player import Player
from enemy import Enemy
from camera import Camera
from collectables import Collectable

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 50)
        self.input_font = pygame.font.Font(None, 40)
        self.options = ["Play", "Sandbox", "Settings", "Quit"]
        self.selected_index = 0

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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.options[self.selected_index] == "Play":
                            self.level_select()
                        elif self.options[self.selected_index] == "Sandbox":
                            self.sandbox_menu()
                        elif self.options[self.selected_index] == "Settings":
                            self.settings_menu()
                        elif self.options[self.selected_index] == "Quit":
                            pygame.quit()
                            sys.exit()
            self.clock.tick(FPS)

    def sandbox_menu(self):
        options = ["Create New", "Load", "Back"]
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if options[selected_option] == "Back":
                            return
                        elif options[selected_option] == "Create New":
                            self.create_new_level()
                        elif options[selected_option] == "Load":
                            self.load_existing_level()
            self.clock.tick(FPS)

    def load_level(self, filename):
        with open(f"levels/{filename}", 'r') as file:
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
                    collectable = Collectable(x, y)
                    collectables.add(collectable)
                    all_sprites.add(collectable)
                elif tile == "E":
                    enemy = Enemy(x, y)
                    enemies.add(enemy)
                    all_sprites.add(enemy)

        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, len(data["level"][0]) * TILE_SIZE,
                             len(data["level"]) * TILE_SIZE)

        self.run_level(all_sprites, player, blocks)

    def run_level(self, all_sprites, player, blocks):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            player.update(blocks)
            self.camera.update(player)

            self.screen.fill(BG_COLOR)
            for sprite in all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))

            pygame.display.flip()
            self.clock.tick(FPS)

    def level_select(self):
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_level = (selected_level + 1) % len(levels)
                    elif event.key == pygame.K_UP:
                        selected_level = (selected_level - 1) % len(levels)
                    elif event.key == pygame.K_RETURN:
                        if levels[selected_level] == "Back":
                            return
                        elif levels[selected_level] == "Level 1":
                            self.load_level("level1.json")
            self.clock.tick(FPS)

    def create_new_level(self):
        sizes = ["20x11", "25x14", "30x17", "35x20", "40x22"]
        selected_size = 0

        while True:
            self.screen.fill(BG_COLOR)
            for i, size in enumerate(sizes):
                color = (255, 255, 255) if i == selected_size else (200, 200, 200)
                text_surface = self.font.render(size, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 60))
                self.screen.blit(text_surface, text_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_size = (selected_size + 1) % len(sizes)
                    elif event.key == pygame.K_UP:
                        selected_size = (selected_size - 1) % len(sizes)
                    elif event.key == pygame.K_RETURN:
                        width, height = map(int, sizes[selected_size].split('x'))
                        name = self.get_input("Enter level name:")
                        self.create_empty_level(name, width, height)
                        return
            self.clock.tick(FPS)

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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return input_text
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isalnum() or event.unicode in ('_', '-'):
                        input_text += event.unicode

    def create_empty_level(self, name, width, height):
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
            "E": "enemy"
        }

        data = {"level": level, "tiles": tiles}
        os.makedirs('levels', exist_ok=True)
        with open(f"levels/{name}.json", 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Level {name} created.")

    def load_existing_level(self):
        levels = [f for f in os.listdir('levels') if f.endswith('.json')]
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_level = (selected_level + 1) % len(levels)
                    elif event.key == pygame.K_UP:
                        selected_level = (selected_level - 1) % len(levels)
                    elif event.key == pygame.K_RETURN:
                        self.load_level(levels[selected_level])
                        return
            self.clock.tick(FPS)

    def settings_menu(self):
        options = ["Controls", "Sound Effects Volume", "Music Volume", "Back"]
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if options[selected_option] == "Back":
                            return
                        else:
                            print(f"Adjusting {options[selected_option]}...")
            self.clock.tick(FPS)