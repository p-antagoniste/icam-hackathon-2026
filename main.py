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

def screns_play(position):
    x, y = position
    arena = ([[1,7,3]
              [4,7,5]
              [6,7,8]])
    hight = 1
    length = 1
    if y == SCREEN_HEIGHT:

# ---------------- PLAYER ----------------

player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_angle = 0  # initial angle
player = load_image(os.path.join(BASE_DIR, "grafiki", "player.png"), player_pos, transparent_color=None)

# ---------------- RANDOM IMAGES SYSTEM ----------------

bonus_files = ["bonus_1.png", "bonus_2.png", "bonus_3.png"]
bonus_points = {"bonus_1.png": 1, "bonus_2.png": -5, "bonus_3.png": 3}

random_images = [
    pygame.image.load(os.path.join(BASE_DIR, "grafiki", f)).convert_alpha() for f in bonus_files
]

current_random_image = None
random_rect = None
current_bonus_name = None  # track which bonus is active

SPAWN_MIN = 10
SPAWN_MAX = 20
SHOW_MIN = 3
SHOW_MAX = 9

next_spawn_time = time.time() + random.randint(SPAWN_MIN, SPAWN_MAX)
hide_time = 0

# ---------------- SCORE ----------------
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

    # --- RANDOM IMAGE LOGIC ---
    if current_random_image is None and now >= next_spawn_time:
        index = random.randint(0, len(random_images)-1)
        current_random_image = random_images[index]
        current_bonus_name = bonus_files[index]
        random_rect = current_random_image.get_rect()
        random_rect.x = random.randint(0, SCREEN_WIDTH - random_rect.width)
        random_rect.y = random.randint(0, SCREEN_HEIGHT - random_rect.height)
        hide_time = now + random.randint(SHOW_MIN, SHOW_MAX)

    if current_random_image is not None and now >= hide_time:
        current_random_image = None
        next_spawn_time = now + random.randint(SPAWN_MIN, SPAWN_MAX)
        current_bonus_name = None

    # --- COLLISION & SCORE ---
    if current_random_image and rotated_rect.colliderect(random_rect):
        score += bonus_points[current_bonus_name]  # apply points
        current_random_image = None
        current_bonus_name = None
        next_spawn_time = now + random.randint(SPAWN_MIN, SPAWN_MAX)

    # --- DRAWING ---
    screen_surface.fill(background_color)
    screen_surface.blit(rotated_player, rotated_rect)

    if current_random_image:
        screen_surface.blit(current_random_image, random_rect)

    # draw score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen_surface.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()
