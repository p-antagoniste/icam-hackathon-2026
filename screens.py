import time
import pygame

import game
from window import screen_surface, font, TEXT_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT
from level import LEVEL_1, draw_level
import player
from player import move_player, draw_player
from fog import draw_fog

# One function per state, called every frame by the game loop in main.py

# ---------------- TRANSITION ----------------
TRANSITION_DURATION = 3  # seconds
transition_start = None  # set on the first frame of the transition

# ---------------- FUNCTIONS ----------------

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
    global transition_start

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
        game.state = "DUNGEON"

def update_and_draw_dungeon():
    # The player keeps moving while an arrow key is held down
    move_player(pygame.key.get_pressed())

    draw_level(LEVEL_1)
    draw_player()
    # player.player_x, not "from player import player_x": that would be a copy that never moves
    draw_fog(player.player_x, player.player_y)

def draw_weaving_screen():
    screen_surface.fill((20, 90, 90))
    draw_state_name("WEAVING")
    textes = ["Chose the weath-in threds "," [1]   Transfer to the acount thread"," [2]   Keep the money and try to find who did this thread"," [3]   Do nothing and leave the dream","Chose a number and press SPACE to confirm your choice."]
    for i, texte in enumerate(textes):
        draw_mission_texte(texte, i * 35)
    last_key = 0
    if pygame.key.get_pressed()[pygame.K_1]:
        last_key = 1
    elif pygame.key.get_pressed()[pygame.K_2]:
        last_key = 2
        print("last_key", last_key)
    elif pygame.key.get_pressed()[pygame.K_3]:
        last_key = 3
    elif pygame.key.get_pressed()[pygame.K_SPACE]:
        print("last_key", last_key)
        if last_key == 1:
            game.state = "WIN"
        elif last_key == 2:
            game.state = "DEMO"
        elif last_key == 3:
            game.state = "DEMO"


def draw_win_screen():
    screen_surface.fill((120, 90, 20))
    draw_state_name("WIN")

def draw_demo_screen():
    screen_surface.fill((20, 90, 90))
    draw_state_name("DEMO")
    textes = ["Sorry you are in the demo ","buy the full game","to chose this way","if you bought it call this number: 1-800-123-4567","if you want to countinue the demo press SPACE to go back to the weaving screen"]
    for i, texte in enumerate(textes):
            draw_mission_texte(texte, i * 35)
    time.sleep(1)  # to avoid the key being pressed too many times
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        game.state = "WEAVING"