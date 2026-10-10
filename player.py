import math
import time
import pygame

import game
from window import screen_surface
from assets import load_sprite, sounds
from level import LEVEL_1, TILE_SIZE, find_tile

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

# ---------------- FUNCTIONS ----------------

def make_glow(radius, color, max_alpha):
    # A soft light disc: opaque-ish in the middle, fading to invisible at the edge.
    # Big circles first, then smaller ones on top, each a bit less transparent.
    glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        alpha = int(max_alpha * (1 - r / radius))
        pygame.draw.circle(glow, (*color, alpha), (radius, radius), r)
    return glow

# Soft cyan light under the player, so the dark cloak stands out on the dark floor
player_glow = make_glow(radius=32, color=(80, 200, 255), max_alpha=170)

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
            if door_try():
                return True  # locked: the door blocks the player like a wall
        elif LEVEL_1[corner_y // TILE_SIZE][corner_x // TILE_SIZE] == "K":
            global have_key
            have_key = True
            sounds["key_pickup"].play()
            # Remove the key from the level, so it can't be picked up again
            LEVEL_1[corner_y // TILE_SIZE] = LEVEL_1[corner_y // TILE_SIZE][:corner_x // TILE_SIZE] + "." + LEVEL_1[corner_y // TILE_SIZE][corner_x // TILE_SIZE + 1:]
    return False

def door_try():
    # Returns True while the door is locked, so it blocks the player
    if have_key:
        # The door is touched several times per frame: open it only once
        if game.state == "DUNGEON":
            sounds["door_open"].play()
            game.state = "WEAVING"
        return False
    # get_num_channels() is 0 when the sound is not already playing:
    # pushing against the door doesn't start a new thud every frame
    if sounds["locked_door_bump"].get_num_channels() == 0:
        sounds["locked_door_bump"].play()
    return True

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

def draw_player():
    # The glow slowly pulses (between 60% and 100% strength), like in a dream
    player_glow.set_alpha(int(204 + 51 * math.sin(time.time() * 3)))
    screen_surface.blit(player_glow, player_glow.get_rect(center=(player_x, player_y)))

    player_image = player_images[player_direction]
    screen_surface.blit(player_image, player_image.get_rect(center=(player_x, player_y)))
