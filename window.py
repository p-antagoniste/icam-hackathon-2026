import pygame

# Everything else needs the window to exist (pictures can only be loaded once it is open),
# so pygame is started here and every file that draws imports this one first
pygame.init()

# ---------------- SCREEN ----------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 720
background_color = [0, 0, 0]

screen_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Dream Weaver")
clock = pygame.time.Clock()

# ---------------- TEXT ----------------
TEXT_COLOR = (255, 255, 255)
font = pygame.font.SysFont(None, 36)
