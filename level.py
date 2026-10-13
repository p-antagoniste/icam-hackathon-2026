from window import screen_surface
from assets import load_sprite

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
LEVEL_2 = [
    "WWWWWWWWWWWWWWWWWWWW",
    "W..................W",
    "W..................W",
    "W...WWWWWWWWWW..W..W",
    "W...W........W..W..W",
    "W...W....W......W..W",
    "W...W....W......WD.W",
    "W...WWWWWWWWWWWWWWWW",
    "W..................W",
    "W..................W",
    "WWWWWWWW...WWWWWW..W",
    "W......W...W....W..W",
    "W......W...W....W..W",
    "WK..W..W.....W..W..W",
    "WWWWW..WWWWWWW..W..W",
    "W...............W..W",
    "W...............W.PW",
    "WWWWWWWWWWWWWWWWWWWW",
]
LEVEL_3 = [
    "WWWWWWWWWWWWWWWWWWWW",
    "W..................W",
    "W..................W",
    "W...WWWWWWWWWW..W..W",
    "W...W........W..W..W",
    "W...W....W......W..W",
    "W...WP...W......WD.W",
    "W...WWWWWWWWWWWWWWWW",
    "W..................W",
    "W..................W",
    "WWWWWWWW...WWWWWW..W",
    "W......W...W....W..W",
    "W......W...W....W..W",
    "WK..W..W.....W..W..W",
    "WWWWW..WWWWWWW..W..W",
    "W...............W..W",
    "W...............W..W",
    "WWWWWWWWWWWWWWWWWWWW",
]
LEVEL_4 = [
    "WWWWWWWWWWWWWWWWWWWW",
    "W..................W",
    "W..................W",
    "W...WWWWWWWWWW..W..W",
    "W...W........W..W..W",
    "W...W....W......W..W",
    "W...W....W......WD.W",
    "W...WWWWWWWWWWWWWWWW",
    "W..................W",
    "W..................W",
    "WWWWWWWW...WWWWWW..W",
    "WP.....W...W....W..W",
    "W......W...W....W..W",
    "WK..W..W.....W..W..W",
    "WWWWW..WWWWWWW..W..W",
    "W...............W..W",
    "W...............W..W",
    "WWWWWWWWWWWWWWWWWWWW",
]
LEVELS = [LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4]
# The map being played now: a copy of a level, so picking up the key changes the copy
# and LEVEL_1 and LEVEL_2 stay as they are for the next game
dungeon_map = list(LEVEL_1)

# ---------------- TILES ----------------

# Pictures made with PixelLab
floor_image = load_sprite("tiles", "floor.png")
# Drawn on top of the floor, one per map letter (P and . are just floor)
tile_images = {
    "W": load_sprite("tiles", "wall.png"),
    "K": load_sprite("objects", "key.png"),
    "D": load_sprite("objects", "door_closed.png"),
}

# ---------------- FUNCTIONS ----------------

def find_tile(level, letter):
    # Return the (column, row) of the first tile with this letter
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile == letter:
                return x, y
    return None

def load_level(number):
    # Copy level number 0 (mission 1) or 1 (mission 2) into the map: the key is back too.
    # [:] changes the list itself, so the files that imported dungeon_map see the new map
    dungeon_map[:] = list(LEVELS[number])


def draw_level(level):
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            position = (x * TILE_SIZE, y * TILE_SIZE)
            # Floor first, so the key and the door have floor around them
            screen_surface.blit(floor_image, position)
            if tile in tile_images:
                screen_surface.blit(tile_images[tile], position)

