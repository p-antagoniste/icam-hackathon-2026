import pygame
import random
import time
import os

pygame.init()
BASE_DIR = os.path.dirname(__file__)

# ---------------- SCREEN ----------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
background_color = [0, 0, 0]

screen_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pierwsza Gra")
clock = pygame.time.Clock()

# ---------------- FUNCTIONS ----------------

def load_image(img_path, position, transparent_color=None):
    """Load image, handle transparency with alpha or colorkey"""
    image = pygame.image.load(img_path).convert_alpha()
    if transparent_color:
        image.set_colorkey(transparent_color)
    rect = image.get_rect(center=position)
    return [image, rect]

def calculate_player_movement(keys):
    speed = 10
    delta_x = 0
    delta_y = 0

    if keys[pygame.K_UP]:
        delta_y -= speed
    if keys[pygame.K_DOWN]:
        delta_y += speed
    if keys[pygame.K_LEFT]:
        delta_x -= speed
    if keys[pygame.K_RIGHT]:
        delta_x += speed

    return delta_x, delta_y

def limit_position(position):
    x, y = position
    x = max(0, min(x, SCREEN_WIDTH))
    y = max(0, min(y, SCREEN_HEIGHT))
    return [x, y]
"""
def screns_play(position):
    x, y = position
    arena = ([[1,7,3]
              [4,7,5]
              [6,7,8]])
    hight = 1
    length = 1
    if y == SCREEN_HEIGHT:
"""
# ---------------- PLAYER ----------------

player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_angle = 0  # initial angle
player = load_image(os.path.join(BASE_DIR, "grafiki", "player.png"), player_pos, transparent_color=None)

# ---------------- RANDOM IMAGES SYSTEM ----------------


score = 0
font = pygame.font.SysFont(None, 36)

# ---------------- GAME LOOP ----------------

game_status = True
while game_status:
    now = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_status = False  

    # --- PLAYER MOVEMENT ---
    pressed_keys = pygame.key.get_pressed()
    delta_x, delta_y = calculate_player_movement(pressed_keys)

    player_pos[0] += delta_x
    player_pos[1] += delta_y
    player_pos = limit_position(player_pos)

    # --- PLAYER ROTATION ---
    if delta_x > 0:
        player_angle = -90
    elif delta_x < 0:
        player_angle = 90
    elif delta_y < 0:
        player_angle = 0
    elif delta_y > 0:
        player_angle = 180

    rotated_player = pygame.transform.rotate(player[0], player_angle)
    rotated_rect = rotated_player.get_rect(center=player_pos)


    # --- COLLISION & SCORE ---


    # --- DRAWING ---
    screen_surface.fill(background_color)
    screen_surface.blit(rotated_player, rotated_rect)

    # draw score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen_surface.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()
