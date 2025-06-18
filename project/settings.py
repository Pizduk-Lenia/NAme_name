import pygame
# Настройки экрана
WIDTH, HEIGHT = 1280, 720  

# Цвета и шрифты
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (30, 60, 120)
LIGHT_BLUE = (70, 130, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("IRON HANDS")

# Шрифты
font_large = pygame.font.SysFont('Arial', 72, bold=True)
font_medium = pygame.font.SysFont('Arial', 48)
font_small = pygame.font.SysFont('Arial', 24)