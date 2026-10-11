import pygame

import player  # player.player_x, not "from player import player_x": that copy would never move
from window import screen_surface
from level import TILE_SIZE

# ---------------- GUARDS ----------------
# Like in Inception, the mind of Mr. Banks defends itself: "projections" walk back and
# forth, always on the same line. They never chase the Weaver

GUARD_SPEED = 2          # pixels per frame: slower than the player (3)
GUARD_HITBOX_SIZE = 28   # the same as the player
GUARD_COLOR = (220, 70, 90)  # red, until the PixelLab picture is used

# Each guard walks back and forth between two tiles: (column, row) -> (column, row).
# Row 10.5 means "between row 10 and row 11": the guard walks on the line between the two
# rows, so it blocks a corridor 2 tiles wide and you must wait for the right moment
GUARD_ROUTES = [
    ((6, 2), (14, 2)),         # top corridor: the easy one, pass on row 1
    ((11, 10.5), (18, 10.5)),  # big room before the door: blocks rows 10 and 11
    ((4, 15.5), (15, 15.5)),   # bottom corridor to the key: blocks rows 15 and 16
]

# One dictionary per guard, filled by reset_guards() below
guards = []

# ---------------- FUNCTIONS ----------------

def tile_center(column, row):
    # The pixels of the middle of a tile
    return (column * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)

def reset_guards():
    # Every guard back at the start of its route (at the start and for a new game)
    guards.clear()
    for start, end in GUARD_ROUTES:
        x, y = tile_center(*start)
        guards.append({"x": x, "y": y, "start": tile_center(*start), "end": tile_center(*end),
                       "going_to_end": True, "direction": "east"})

reset_guards()

def move_guards():
    for guard in guards:
        if guard["going_to_end"]:
            target_x, target_y = guard["end"]
        else:
            target_x, target_y = guard["start"]
        # Arrived (or less than one step left): stand on the end and turn around
        if abs(target_x - guard["x"]) + abs(target_y - guard["y"]) <= GUARD_SPEED:
            guard["x"], guard["y"] = target_x, target_y
            guard["going_to_end"] = not guard["going_to_end"]
        # Otherwise one step towards it (a route is a straight line: only x or only y changes)
        elif target_x > guard["x"]:
            guard["x"] += GUARD_SPEED
            guard["direction"] = "east"
        elif target_x < guard["x"]:
            guard["x"] -= GUARD_SPEED
            guard["direction"] = "west"
        elif target_y > guard["y"]:
            guard["y"] += GUARD_SPEED
            guard["direction"] = "south"
        else:
            guard["y"] -= GUARD_SPEED
            guard["direction"] = "north"

def guard_hitbox(guard):
    # A box around the guard, like player_hitbox() for the player
    hitbox = pygame.Rect(0, 0, GUARD_HITBOX_SIZE, GUARD_HITBOX_SIZE)
    hitbox.center = (guard["x"], guard["y"])
    return hitbox

def guard_catches_player():
    # True if the box of the player touches the box of a guard
    player_box = player.player_hitbox(player.player_x, player.player_y)
    for guard in guards:
        if player_box.colliderect(guard_hitbox(guard)):
            return True
    return False

def draw_guards():
    for guard in guards:
        pygame.draw.rect(screen_surface, GUARD_COLOR, guard_hitbox(guard))
