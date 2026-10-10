import math
import pygame

from window import screen_surface, SCREEN_WIDTH, SCREEN_HEIGHT
from level import LEVEL_1, TILE_SIZE

# ---------------- FOG OF WAR ----------------
# Dreams are blurry: only the area around the player can be seen,
# and the walls hide what is behind them

FOG_COLOR = (10, 5, 25)  # very dark purple, like the night sky of the dream
FOG_RADIUS = 150         # pixels: how far the player can see
FOG_CLEAR_RADIUS = 60    # pixels: inside this circle there is no fog at all
RAY_COUNT = 180          # rays sent all around the player (one every 2 degrees)
RAY_STEP = 4             # pixels: how far a ray moves before checking for a wall again
BLOCKS_VIEW = "WD"       # tiles that block the view: walls and the door

# ---------------- FUNCTIONS ----------------

def make_fog():
    # A fog layer twice as big as the screen, with a hole in its middle.
    # Each frame it is moved so the hole is on the player: one blit, no redrawing.
    fog = pygame.Surface((SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2), pygame.SRCALPHA)
    fog.fill((*FOG_COLOR, 255))
    center = (SCREEN_WIDTH, SCREEN_HEIGHT)
    # Big circles first, then smaller ones on top, each a bit more transparent:
    # the fog fades out softly towards the player
    for r in range(FOG_RADIUS, 0, -1):
        if r <= FOG_CLEAR_RADIUS:
            alpha = 0
        else:
            alpha = int(255 * (r - FOG_CLEAR_RADIUS) / (FOG_RADIUS - FOG_CLEAR_RADIUS))
        pygame.draw.circle(fog, (*FOG_COLOR, alpha), center, r)
    return fog

fog_layer = make_fog()
# The fog of the current frame, made again each frame from the rays and fog_layer
fog_mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

def cast_ray(start_x, start_y, angle):
    # Walk from the player in one direction until a wall is hit (or FOG_RADIUS is reached).
    # Returns the last point reached, and the wall tile hit (None if no wall was hit)
    step_x = math.cos(angle) * RAY_STEP
    step_y = math.sin(angle) * RAY_STEP
    x, y = start_x, start_y
    for _ in range(FOG_RADIUS // RAY_STEP):
        x += step_x
        y += step_y
        column, row = int(x // TILE_SIZE), int(y // TILE_SIZE)
        if LEVEL_1[row][column] in BLOCKS_VIEW:
            return (x, y), (column, row)
    return (x, y), None

def draw_fog(player_x, player_y):
    # Drawn last, on top of the maze and the player

    # 1. Send rays all around: together their end points draw the shape the player can see
    visible_points = []
    walls_seen = set()  # a set: each wall tile is kept only once
    for i in range(RAY_COUNT):
        point, wall = cast_ray(player_x, player_y, 2 * math.pi * i / RAY_COUNT)
        visible_points.append(point)
        if wall is not None:
            walls_seen.add(wall)

    # The rays sometimes slip past the corner tile of a wall (where two walls meet), so it
    # blinks. Fix: when two seen walls touch by their corners, the walls between them are seen too
    for column, row in list(walls_seen):
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            if (column + dx, row + dy) in walls_seen:
                for between in [(column + dx, row), (column, row + dy)]:
                    if LEVEL_1[between[1]][between[0]] in BLOCKS_VIEW:
                        walls_seen.add(between)

    # 2. Full fog everywhere, then cut out (alpha 0 = transparent) what the player can see:
    #    the shape of the rays, and the whole wall tiles they hit (so the walls show, but
    #    not what is behind them)
    fog_mask.fill((*FOG_COLOR, 255))
    pygame.draw.polygon(fog_mask, (*FOG_COLOR, 0), visible_points)
    for column, row in walls_seen:
        fog_mask.fill((*FOG_COLOR, 0), (column * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # 3. Add the soft round fog on top, so the view still fades out far from the player
    fog_mask.blit(fog_layer, fog_layer.get_rect(center=(player_x, player_y)))

    screen_surface.blit(fog_mask, (0, 0))
