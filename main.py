import pygame
import time
import math
import os

pygame.init()
BASE_DIR = os.path.dirname(__file__)

# ---------------- SCREEN ----------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 720
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
TILE_SIZE = 40  # 20 columns x 18 rows on an 800 x 720 screen

# W = wall, . = floor, P = player start, K = key, D = door
LEVEL_1 = [
    "WWWWWWWWWWWWWWWWWWWW",
    "WP..W...........W..W",
    "W...W...........W..W",
    "W...W..WWWWWWW..W..W",
    "W...W........W.....W",
    "W............W.....W",
    "W.........WWWWWW...W",
    "W.........W........W",
    "WWWWWW....W........W",
    "W.KW......W...WWWWWW",
    "W..W......W........W",
    "W..W...WWWW........W",
    "W..W...W.......W...W",
    "W..W...W.......W.D.W",
    "W..WWWWW.......WWWWW",
    "W..................W",
    "W..................W",
    "WWWWWWWWWWWWWWWWWWWW",
]

# ---------------- FUNCTIONS ----------------

def load_sprite(*path_parts):
    # Load a PNG from the grafiki folder, keeping its transparency
    return pygame.image.load(os.path.join(BASE_DIR, "grafiki", *path_parts)).convert_alpha()

def make_glow(radius, color, max_alpha):
    # A soft light disc: opaque-ish in the middle, fading to invisible at the edge.
    # Big circles first, then smaller ones on top, each a bit less transparent.
    glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        alpha = int(max_alpha * (1 - r / radius))
        pygame.draw.circle(glow, (*color, alpha), (radius, radius), r)
    return glow

def player_hitbox(x, y):
    # A box a bit smaller than a tile, so the player slips easily into corridors
    hitbox = pygame.Rect(0, 0, PLAYER_HITBOX_SIZE, PLAYER_HITBOX_SIZE)
    hitbox.center = (x, y)
    return hitbox

def hits_wall(hitbox):
    # The hitbox is smaller than a tile, so checking its 4 corners is enough
    # (-1 because right and bottom are the first pixels just outside the box)
    left, right = hitbox.left, hitbox.right - 1
    top, bottom = hitbox.top, hitbox.bottom - 1
    for corner_x, corner_y in [(left, top), (right, top), (left, bottom), (right, bottom)]:
        if LEVEL_1[corner_y // TILE_SIZE][corner_x // TILE_SIZE] == "W":
            return True
        elif LEVEL_1[corner_y // TILE_SIZE][corner_x // TILE_SIZE] == "D":
            door_try()
        elif LEVEL_1[corner_y // TILE_SIZE][corner_x // TILE_SIZE] == "K":
            global have_key
            have_key = True
            # Remove the key from the level, so it can't be picked up again
            LEVEL_1[corner_y // TILE_SIZE] = LEVEL_1[corner_y // TILE_SIZE][:corner_x // TILE_SIZE] + "." + LEVEL_1[corner_y // TILE_SIZE][corner_x // TILE_SIZE + 1:]
    return False

def move_player(keys):
    global player_x, player_y, player_direction
    delta_x = 0
    delta_y = 0

    if keys[pygame.K_UP]:
        delta_y = -1
        player_direction = "north"
    if keys[pygame.K_DOWN]:
        delta_y = 1
        player_direction = "south"
    if keys[pygame.K_LEFT]:
        delta_x = -1
        player_direction = "west"
    if keys[pygame.K_RIGHT]:
        delta_x = 1
        player_direction = "east"

    # Move one pixel at a time, so the player stops right against a wall.
    # x and y are checked separately: blocked on one side, the player slides along the wall.
    for _ in range(PLAYER_SPEED):
        if not hits_wall(player_hitbox(player_x + delta_x, player_y)):
            player_x += delta_x
        if not hits_wall(player_hitbox(player_x, player_y + delta_y)):
            player_y += delta_y

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
            position = (x * TILE_SIZE, y * TILE_SIZE)
            # Floor first, so the key and the door have floor around them
            screen_surface.blit(floor_image, position)
            if tile in tile_images:
                screen_surface.blit(tile_images[tile], position)

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
    # The player keeps moving while an arrow key is held down
    move_player(pygame.key.get_pressed())

    draw_level(LEVEL_1)

    # The glow slowly pulses (between 60% and 100% strength), like in a dream
    player_glow.set_alpha(int(204 + 51 * math.sin(time.time() * 3)))
    screen_surface.blit(player_glow, player_glow.get_rect(center=(player_x, player_y)))

    player_image = player_images[player_direction]
    screen_surface.blit(player_image, player_image.get_rect(center=(player_x, player_y)))

def draw_weaving_screen():
    screen_surface.fill((20, 90, 90))
    draw_state_name("WEAVING")

def draw_win_screen():
    screen_surface.fill((120, 90, 20))
    draw_state_name("WIN")

def door_try():
        if have_key:
            draw_weaving_screen()
# ---------------- TILES ----------------

# Pictures made with PixelLab
floor_image = load_sprite("tiles", "floor.png")
# Drawn on top of the floor, one per map letter (P and . are just floor)
tile_images = {
    "W": load_sprite("tiles", "wall.png"),
    "K": load_sprite("objects", "key.png"),
    "D": load_sprite("objects", "door_closed.png"),
}

# ---------------- PLAYER ----------------

PLAYER_SPEED = 3         # pixels per frame (x 60 frames = 180 pixels per second)
PLAYER_HITBOX_SIZE = 28  # smaller than a tile (40) to move easily in corridors
have_key = False  # the player starts without the key

# The position is in pixels: the centre of the player, starting in the middle of the P tile
start_column, start_row = find_tile(LEVEL_1, "P")
player_x = start_column * TILE_SIZE + TILE_SIZE // 2
player_y = start_row * TILE_SIZE + TILE_SIZE // 2
player_direction = "south"  # facing the camera at the start

# One picture per direction, made with PixelLab
player_images = {
    "south": load_sprite("player", "south.png"),
    "north": load_sprite("player", "north.png"),
    "east": load_sprite("player", "east.png"),
    "west": load_sprite("player", "west.png"),
}

# Soft cyan light under the player, so the dark cloak stands out on the dark floor
player_glow = make_glow(radius=32, color=(80, 200, 255), max_alpha=170)


font = pygame.font.SysFont(None, 36)

# ---------------- MUSIC ----------------

# Dreamy background music made with Suno, played on a loop (-1) during the whole game
pygame.mixer.music.load(os.path.join(BASE_DIR, "music", "Inception Heist.mp3"))
pygame.mixer.music.set_volume(0.5)  # 0 = silent, 1 = full volume
pygame.mixer.music.play(-1)

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
