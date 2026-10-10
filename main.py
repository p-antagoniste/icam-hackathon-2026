import pygame
import time
import os

pygame.init()
BASE_DIR = os.path.dirname(__file__)

# ---------------- SCREEN ----------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
background_color = [0, 0, 0]

screen_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Dream Weaver")
clock = pygame.time.Clock()

# ---------------- STATES ----------------
# The game is always on exactly one of these screens, in this order
STATES = ["MISSION", "TRANSITION", "DUNGEON", "WEAVING", "WIN"]
TEXT_COLOR = (255, 255, 255)

# ---------------- FUNCTIONS ----------------

def load_image(img_path, position, transparent_color=None):
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

def next_state(current_state):
    # After the last state, go back to the first one
    index = STATES.index(current_state)
    return STATES[(index + 1) % len(STATES)]

def draw_state_name(name):
    text = font.render(name, True, TEXT_COLOR)
    screen_surface.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, 40)))

def draw_mission_texte(texte, bonus):
    text = font.render(texte, True, TEXT_COLOR)
    screen_surface.blit(text, text.get_rect( midtop=(SCREEN_WIDTH - 400, 80 + bonus)))

def draw_mission_screen():
    screen_surface.fill((15, 10, 30))
    draw_state_name("MISSION")
    textes = ["INCOMING MESSAGE (sender: unknown)"," Target:   Mr. Banks, senior banker."," Mission:  Enter his dream tonight.","          Make him believe he must transfer","          1,000,000 € to account FR76 ... 0042."," Payment:  generous."," Press SPACE to accept the mission."]
    for i, texte in enumerate(textes):
        draw_mission_texte(texte, i * 25)

def draw_transition_screen():
    screen_surface.fill((60, 20, 90))
    draw_state_name("TRANSITION")

def update_and_draw_dungeon():
    global player_pos, player_angle

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

    # --- DRAWING ---
    screen_surface.fill((20, 25, 70))
    screen_surface.blit(rotated_player, rotated_rect)
    draw_state_name("DUNGEON")

def draw_weaving_screen():
    screen_surface.fill((20, 90, 90))
    draw_state_name("WEAVING")

def draw_win_screen():
    screen_surface.fill((120, 90, 20))
    draw_state_name("WIN")

# ---------------- PLAYER ----------------

player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
player_angle = 0  # initial angle
player = load_image(os.path.join(BASE_DIR, "grafiki", "player.png"), player_pos, transparent_color=None)


font = pygame.font.SysFont(None, 36)

# ---------------- GAME LOOP ----------------

state = "MISSION"

game_status = True
while game_status:
    now = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_status = False
        # Temporary: SPACE goes to the next state, to test the skeleton
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            state = next_state(state)

    if state == "MISSION":
        draw_mission_screen()
    elif state == "TRANSITION":
        draw_transition_screen()
    elif state == "DUNGEON":
        update_and_draw_dungeon()
    elif state == "WEAVING":
        draw_weaving_screen()
    elif state == "WIN":
        draw_win_screen()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()
