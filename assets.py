import os
import pygame

import window  # the window must be open before loading pictures

BASE_DIR = os.path.dirname(__file__)

# ---------------- FUNCTIONS ----------------

def load_sprite(*path_parts):
    # Load a PNG from the grafiki folder, keeping its transparency
    return pygame.image.load(os.path.join(BASE_DIR, "grafiki", *path_parts)).convert_alpha()

def load_background(*path_parts):
    # Load a full-screen picture from the grafiki folder: scaled so it covers the whole
    # window, and the parts that stick out on the sides (or top and bottom) are cut off
    picture = pygame.image.load(os.path.join(BASE_DIR, "grafiki", *path_parts)).convert()
    scale = max(window.SCREEN_WIDTH / picture.get_width(), window.SCREEN_HEIGHT / picture.get_height())
    size = (round(picture.get_width() * scale), round(picture.get_height() * scale))
    picture = pygame.transform.smoothscale(picture, size)
    visible = pygame.Rect(0, 0, window.SCREEN_WIDTH, window.SCREEN_HEIGHT)
    visible.center = (size[0] // 2, size[1] // 2)
    return picture.subsurface(visible).copy()

def load_animation(*path_parts):
    # Load every picture of an animated GIF from the grafiki folder, keeping their transparency
    # (load_animation gives (picture, duration) pairs: only the pictures are kept)
    frames = pygame.image.load_animation(os.path.join(BASE_DIR, "grafiki", *path_parts))
    return [picture.convert_alpha() for picture, duration in frames]

def load_sound(name):
    # Load an MP3 from the sound folder
    return pygame.mixer.Sound(os.path.join(BASE_DIR, "sound", name + ".mp3"))

def start_music():
    # Dreamy background music made with Suno, played on a loop (-1) during the whole game
    pygame.mixer.music.load(os.path.join(BASE_DIR, "music", "Inception Heist.mp3"))
    pygame.mixer.music.set_volume(0.5)  # 0 = silent, 1 = full volume
    pygame.mixer.music.play(-1)

# ---------------- SOUNDS ----------------

# Sound effects made with ElevenLabs
sounds = {
    "key_pickup": load_sound("key_pickup"),
    "door_open": load_sound("door_open"),
    "locked_door_bump": load_sound("locked_door_bump"),
    "entering_dream": load_sound("entering_dream"),
    "weaving_dream": load_sound("weaving_dream"),
}

# Played once when a screen starts
SCREEN_SOUNDS = {
    "TRANSITION": "entering_dream",
    "WEAVING": "weaving_dream",
}
