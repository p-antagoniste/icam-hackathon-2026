import pygame
import time

import game
from window import clock
from assets import sounds, SCREEN_SOUNDS, start_music
from screens import (
    draw_mission_screen,
    draw_transition_screen,
    update_and_draw_dungeon,
    draw_weaving_screen,
    draw_win_screen,
)

# The game is split in small files:
#   window.py   the window, the clock and the font
#   game.py     the list of states and the current one (game.state)
#   assets.py   loading pictures and sounds, the music
#   level.py    the dungeon map and how to draw it
#   player.py   the player: moving, walls, key and door
#   fog.py      the fog of war around the player
#   screens.py  what to draw on each screen

start_music()

# ---------------- GAME LOOP ----------------

previous_state = None  # to notice when the screen changes

game_status = True
while game_status:
    now = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_status = False
        # Temporary: SPACE goes to the next state, to test the skeleton
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game.state = game.next_state(game.state)

    # A new screen just started: play its sound once
    if game.state != previous_state:
        if game.state in SCREEN_SOUNDS:
            sounds[SCREEN_SOUNDS[game.state]].play()
        previous_state = game.state

    if game.state == "MISSION":
        draw_mission_screen()
    elif game.state == "TRANSITION":
        draw_transition_screen()
    elif game.state == "DUNGEON":
        update_and_draw_dungeon()
    elif game.state == "WEAVING":
        draw_weaving_screen()
    elif game.state == "WIN":
        draw_win_screen()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()
