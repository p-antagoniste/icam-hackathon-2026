import math
import time
import pygame

import player  # player.player_x, not "from player import player_x": that copy would never move
import game  # game.state, not "from game import state": that copy would never change
from window import screen_surface
from assets import load_sprite, load_animation
from level import TILE_SIZE

# ---------------- GUARDS ----------------
# Like in Inception, the mind of Mr. Banks defends itself: "projections" walk back and
# forth, always on the same line. They never chase the Weaver

GUARD_SPEED = 2          # pixels per frame: slower than the player (3)
GUARD_HITBOX_SIZE = 28   # the same as the player
GUARD_FRAME_DURATION = 0.15  # seconds per picture of the walk: slower than the player (0.1)
GUARD_GLOW_COLOR = (220, 70, 90)  # red, the opposite of the cyan glow of the player
GUARD_PENALTY = 15       # seconds of dream lost when a guard touches the Weaver
GUARD_PROTECTION = 2     # seconds after a touch when the guards can't touch the Weaver again
GUARD_HEAR_DISTANCE = 200  # pixels: closer than this, the whispers of a guard can be heard

# Each guard walks back and forth between two tiles: (column, row) -> (column, row).
# Row 10.5 means "between row 10 and row 11": the guard walks on the line between the two
# rows, so it blocks a corridor 2 tiles wide and you must wait for the right moment
GUARD_ROUTES = [
    [((4, 1.5), (14, 1.5)),         # top corridor: the easy one, pass on row 1
    ((11, 10.5), (18, 10.5)),  # big room before the door: blocks rows 10 and 11
    ((4, 15.5), (15, 15.5)),],   # bottom corridor to the key: blocks rows 15 and 16
    [((1, 15.5), (15, 15.5)),         # top corridor: the easy one, pass on row 1
    ((1, 8.5), (19, 8.5)),  # big room before the door: blocks rows 10 and 11
    ((15, 1), (15, 6)),
    ((6, 1.5), (19, 1.5)),]
]

# One dictionary per guard, filled by reset_guards() below
guards = []
last_touch = None  # when a guard last touched the Weaver (None = not yet)

# One picture per direction, made with PixelLab
guard_images = {
    "south": load_sprite("guard", "south.png"),
    "north": load_sprite("guard", "north.png"),
    "east": load_sprite("guard", "east.png"),
    "west": load_sprite("guard", "west.png"),
}
# Walking animations (8 pictures each), made with PixelLab.
# A direction without one would keep its still picture
guard_walking_images = {
    "south": load_animation("guard", "walking_south.gif"),
    "north": load_animation("guard", "walking_north.gif"),
    "east": load_animation("guard", "walking_east.gif"),
    "west": load_animation("guard", "walking_west.gif"),
}

# Soft red light under each guard, like the cyan one under the player
guard_glow = player.make_glow(radius=32, color=GUARD_GLOW_COLOR, max_alpha=150)

# ---------------- FUNCTIONS ----------------

def tile_center(column, row):
    # The pixels of the middle of a tile
    return (column * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)

def reset_guards():
    # Every guard back at the start of its route (at the start and for a new game)
    global last_touch
    last_touch = None
    guards.clear()
    for start, end in GUARD_ROUTES[game.mission_number]:
        x, y = tile_center(*start)
                # At the start, the guard looks towards the end of its route
        if end[0] > start[0]:
            direction = "east"
        elif end[0] < start[0]:
            direction = "west"
        elif end[1] > start[1]:
            direction = "south"
        else:
            direction = "north"
        guards.append({"x": x, "y": y, "start": tile_center(*start), "end": tile_center(*end),
                       "going_to_end": True, "direction": direction})

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

def player_is_protected():
    # Just after a touch, the Weaver is safe for a moment. Without this, a guard walking
    # through the Weaver would touch him again every frame and take all the time at once
    return last_touch is not None and time.time() - last_touch < GUARD_PROTECTION

def guard_touches_player():
    # True if the box of the player touches the box of a guard, but only once per touch:
    # after it, the Weaver is protected for GUARD_PROTECTION seconds
    global last_touch
    if player_is_protected():
        return False
    player_box = player.player_hitbox(player.player_x, player.player_y)
    for guard in guards:
        if player_box.colliderect(guard_hitbox(guard)):
            last_touch = time.time()
            return True
    return False

def guard_is_near():
    # True if a guard is close to the player. The fog hides the guards, but not their
    # whispers: it warns the player before a guard can be seen (even behind a wall)
    for guard in guards:
        if math.hypot(guard["x"] - player.player_x, guard["y"] - player.player_y) < GUARD_HEAR_DISTANCE:
            return True
    return False

def draw_guards():
    for guard in guards:
        center = (guard["x"], guard["y"])
        screen_surface.blit(guard_glow, guard_glow.get_rect(center=center))

        # The guards never stop: always show the walking animation, if there is one
        if guard["direction"] in guard_walking_images:
            frames = guard_walking_images[guard["direction"]]
            guard_image = frames[int(time.time() / GUARD_FRAME_DURATION) % len(frames)]
        else:
            guard_image = guard_images[guard["direction"]]
        screen_surface.blit(guard_image, guard_image.get_rect(center=center))
