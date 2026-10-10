import pygame
import time
import os

pygame.init()
BASE_DIR = os.path.dirname(__file__)

# ---------------- SCREEN ----------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
background_color = [0, 0, 0]

screen_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Dream Weaver")
clock = pygame.time.Clock()

# ---------------- STATES ----------------
# The game is always on exactly one of these screens, in this order
STATES = ["MISSION", "TRANSITION", "DUNGEON", "WEAVING", "WIN"]
TEXT_COLOR = (255, 255, 255)

# ---------------- TRANSITION ----------------
TRANSITION_DURATION = 3  # seconds
transition_start = None  # set on the first frame of the transition

# ---------------- DUNGEON ----------------
TILE_SIZE = 40  # 20 columns x 20 rows on an 800 x 800 screen

# W = wall, . = floor, P = player start, K = key, D = door
LEVEL_1 = [
    "WWWWWWWWWWWWWWWWWWWW",
    "WP.....W...........W",
    "W.WWWW.W.WWWWWWWWW.W",
    "W.W....W.........W.W",
    "W.W.WWWWWWWWWWWW.W.W",
    "W.W......W.....W.W.W",
    "W.WWWWWW.W.WWW.W.W.W",
    "W......W.W..KW.....W",
    "WWWWWW.W.WWWWW.WWWWW",
    "W......W.......W...W",
    "W.WWWWWWWWWWWW.W.W.W",
    "W..............W.W.W",
    "WWWWWWWWWWWWW.WW.W.W",
    "W.......W........W.W",
    "W.WWWWW.W.WWWWWWWWWW",
    "W.W...W.W.W........W",
    "W.W.W.W...W.WWWWWW.W",
    "W...W.WWWWW.W....W.W",
    "WWWWW.........WW.W.D",
    "WWWWWWWWWWWWWWWWWWWW",
]

FLOOR_COLOR = (20, 25, 70)  # dark blue
TILE_COLORS = {
    "W": (60, 20, 90),    # dark purple
    "K": (240, 200, 40),  # yellow
    "D": (120, 70, 30),   # brown
}

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

def find_tile(level, letter):
    # Return the (column, row) of the first tile with this letter
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile == letter:
                return x, y
    return None

def draw_level(level):
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            color = TILE_COLORS.get(tile, FLOOR_COLOR)  # P and . are floor
            pygame.draw.rect(screen_surface, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

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
        draw_mission_texte(texte, i * 35)

def draw_transition_screen():
    global state, transition_start

    # Remember the time on the first frame of the transition
    if transition_start is None:
        transition_start = time.time()

    # progress goes from 0 (start) to 1 (end of the transition)
    progress = (time.time() - transition_start) / TRANSITION_DURATION

    # A circle grows from the centre with rings inside: we fall into the dream
    # (600 = a bit more than the distance from the centre to a corner)
    screen_surface.fill((15, 10, 30))
    center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.draw.circle(screen_surface, (60, 20, 90), center, int(progress * 600))
    for i in range(1, 6):
        ring_radius = int(progress * 600) - i * 70
        if ring_radius > 0:
            pygame.draw.circle(screen_surface, (150, 90, 220), center, ring_radius, 3)

    text = font.render("Entering the dream of Mr. Banks...", True, TEXT_COLOR)
    screen_surface.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)))

    # When the transition is over, go to the dungeon
    if progress >= 1:
        transition_start = None  # ready for the next game
        state = "DUNGEON"

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
    draw_level(LEVEL_1)
    screen_surface.blit(rotated_player, rotated_rect)

def draw_weaving_screen():
    screen_surface.fill((20, 90, 90))
    draw_state_name("WEAVING")

def draw_win_screen():
    screen_surface.fill((120, 90, 20))
    draw_state_name("WIN")

# ---------------- PLAYER ----------------

# Start in the middle of the P tile
start_x, start_y = find_tile(LEVEL_1, "P")
player_pos = [start_x * TILE_SIZE + TILE_SIZE // 2, start_y * TILE_SIZE + TILE_SIZE // 2]
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
