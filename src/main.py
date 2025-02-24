import pygame
import sys
from settings import *
from menu import Menu

# Initialize Pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.get_surface().get_size()

pygame.display.set_caption("Platformer Game")

# Start the main menu
menu = Menu(screen)
menu.main_menu()

# Quit the game
pygame.quit()
sys.exit()
