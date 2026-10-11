import math
import time
import pygame

import game
from window import screen_surface, font, TEXT_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT
from level import LEVEL_1, draw_level, load_level
import player
from player import move_player, draw_player, reset_player
from guards import (move_guards, draw_guards, guard_touches_player, player_is_protected,
                    guard_is_near, reset_guards, GUARD_PENALTY)
from fog import draw_fog
import loom  # loom.loom_start, not "from loom import loom_start": that copy would never change
from assets import load_background, load_picture, sounds, start_music

# One function per state, called every frame by the game loop in main.py

# ---------------- TITLE ----------------
# Made with Gemini: the bottom of the picture is left empty for the "Press SPACE" text
title_image = load_background("title_screen.jpeg")

# ---------------- MISSION ----------------
# Made with Gemini too. Their dark background is the same colour as the screen,
# so only the video call and the photo can be seen
PORTRAIT_SIZE = 300   # pixels (the pictures are 1024 x 1024, made smaller)
PORTRAIT_TOP = 30     # pixels from the top of the screen
LABEL_Y = 330         # where the text under the pictures goes
MESSAGE_Y = 530       # the middle of the mission text, under the pictures
MISSION_BACKGROUND = (11, 7, 31)  # the colour around the pictures, so their edges can't be seen
CLIENT_COLOR = (80, 200, 255)  # cyan, like the video call
TARGET_COLOR = (220, 70, 90)   # red, like the circle around his face
THE_VICTORY_NUMBER = 0
client_image = load_picture((PORTRAIT_SIZE, PORTRAIT_SIZE), "anonymous_client.jpeg")
banks_image = load_picture((PORTRAIT_SIZE, PORTRAIT_SIZE), "mr_banks.jpeg")

# ---------------- WIN ----------------
# Made with Gemini: the next morning, Mr. Banks sends the money. The bottom of the
# picture (the front of the desk) is dark and simple, so the message goes there
win_image1 = load_background("win_screen.jpeg")
win_image2 = load_background("find anonime.jpg")
win_image3 = load_background("second try.jpg")

WIN_MESSAGE_Y = 612  # the middle of the message, low enough to not hide Mr. Banks

# ---------------- WAKE UP ----------------
# Made with Gemini: Mr. Banks wakes up and the dream threads break. Like the win
# picture, its bottom is dark and empty, so the message goes at WIN_MESSAGE_Y too
wake_up_image = load_background("wake_up.jpeg")

# ---------------- TRANSITION ----------------
TRANSITION_DURATION = 3  # seconds
transition_start = None  # set on the first frame of the transition

# ---------------- WEAVING ----------------
WEAVING_DURATION = 3     # seconds to weave all the threads
THREAD_GROW_TIME = 0.4   # seconds for one thread to cross the whole screen
THREAD_SPACING = 80      # pixels between two threads
THREAD_WIDTH = 12        # pixels
# Gold, cyan, red and purple, like the thread spools in grafiki/objects
THREAD_COLORS = [(230, 190, 90), (80, 200, 255), (220, 70, 90), (150, 90, 220)]
weaving_start = None  # set on the first frame of the weaving

# The threads, in the order they appear: one vertical, one horizontal, one vertical...
VERTICAL_THREADS = list(range(THREAD_SPACING // 2, SCREEN_WIDTH, THREAD_SPACING))     # their x
HORIZONTAL_THREADS = list(range(THREAD_SPACING // 2, SCREEN_HEIGHT, THREAD_SPACING))  # their y
THREADS = []
for i in range(max(len(VERTICAL_THREADS), len(HORIZONTAL_THREADS))):
    if i < len(VERTICAL_THREADS):
        THREADS.append(("vertical", i))
    if i < len(HORIZONTAL_THREADS):
        THREADS.append(("horizontal", i))

# ---------------- MESSAGES ----------------
# A "typewriter" font: every letter has the same width, so the spaces at the start of the
# lines make columns (the first of these fonts found on the computer is used)
MESSAGE_FONT_NAMES = "menlo,consolas,dejavusansmono,couriernew"
MESSAGE_FONT_SIZES = [26, 25, 24, 23, 22, 21, 20]  # the biggest size where the lines fit is used
MESSAGE_PADDING = 24                                # pixels between the text and the panel border
MESSAGE_MAX_WIDTH = SCREEN_WIDTH - 4 * MESSAGE_PADDING
MESSAGE_TITLE_COLOR = (230, 190, 90)                # gold, for the first line
MESSAGE_PANEL_COLOR = (10, 5, 25, 235)              # very dark purple, a bit transparent
MESSAGE_BORDER_COLOR = (150, 90, 220)
message_fonts = {}  # one font per size, made only once
Dream_time = 60
dungeon_start = None
time_lost = 0  # seconds taken away by the guards: Mr. Banks wakes up sooner
# ---------------- FUNCTIONS ----------------

def message_font(size):
    if size not in message_fonts:
        message_fonts[size] = pygame.font.SysFont(MESSAGE_FONT_NAMES, size)
    return message_fonts[size]

def wrap_line(line, text_font):
    # Cut a line that is too wide into several lines, between two words.
    # The new lines start with the same spaces, so they stay in the same column.
    indent = line[:len(line) - len(line.lstrip())]
    lines = [""]
    for i, word in enumerate(line.split(" ")):
        if i == 0:
            lines[-1] = word
        elif word and lines[-1].strip() and text_font.size(lines[-1] + " " + word)[0] > MESSAGE_MAX_WIDTH:
            lines.append(indent + word)
        else:
            lines[-1] += " " + word
    return lines

def draw_message(lines, center_y=SCREEN_HEIGHT // 2):
    # Draw a message in a dark panel so it is easy to read on any background.
    # The lines are aligned on the left, the first one is the title and the last one
    # (the key to press) slowly blinks, with a bit of space around them.

    # The biggest font where every line fits. If none, the smallest, and cut the long lines
    for size in MESSAGE_FONT_SIZES:
        text_font = message_font(size)
        if all(text_font.size(line)[0] <= MESSAGE_MAX_WIDTH for line in lines):
            break
    line_height = text_font.get_linesize() + 6
    gap = line_height // 2  # the extra space after the title and before the last line

    # The pictures of the lines, with where they go (y from the top of the text)
    pictures = []
    y = 0
    for i, line in enumerate(lines):
        is_title = i == 0 and len(lines) > 1
        is_last = i == len(lines) - 1 and len(lines) > 2
        if is_last:
            y += gap
        color = TEXT_COLOR
        if is_title:
            color = MESSAGE_TITLE_COLOR
        elif is_last:
            # Between 55% and 100% bright
            brightness = 0.775 + 0.225 * math.sin(time.time() * 4)
            color = [int(c * brightness) for c in TEXT_COLOR]
        for part in wrap_line(line, text_font):
            pictures.append((text_font.render(part.rstrip(), True, color), y))
            y += line_height
        if is_title:
            y += gap

    # The panel, just big enough for the widest line
    text_width = max(picture.get_width() for picture, y in pictures)
    panel = pygame.Rect(0, 0, text_width + 2 * MESSAGE_PADDING, y - 6 + 2 * MESSAGE_PADDING)
    panel.center = (SCREEN_WIDTH // 2, center_y)
    panel_surface = pygame.Surface(panel.size, pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, MESSAGE_PANEL_COLOR, panel_surface.get_rect(), border_radius=12)
    screen_surface.blit(panel_surface, panel)
    pygame.draw.rect(screen_surface, MESSAGE_BORDER_COLOR, panel, 2, border_radius=12)

    for picture, y in pictures:
        screen_surface.blit(picture, (panel.left + MESSAGE_PADDING, panel.top + MESSAGE_PADDING + y))

def draw_label(words, color, center):
    # A dark shadow under the text, so it can be read on any background
    shadow = font.render(words, True, (10, 5, 25))
    screen_surface.blit(shadow, shadow.get_rect(center=(center[0] + 2, center[1] + 2)))
    text = font.render(words, True, color)
    screen_surface.blit(text, text.get_rect(center=center))

def draw_state_name(name, color=TEXT_COLOR):
    # A text at the top of the screen, white if no color is given
    draw_label(name, color, (SCREEN_WIDTH // 2, 40))

def reset_game():
    # Everything back to the start, to play again
    global weaving_start
    global dungeon_start, time_lost
    dungeon_start = None
    time_lost = 0
    load_level(0)   # the key is back in the maze
    reset_player()  # the player is back on P, without the key
    reset_guards()  # the guards are back at the start of their route
    loom.reset_loom()  # the weaving song is back at the start
    weaving_start = None

def draw_title_screen():
    screen_surface.blit(title_image, (0, 0))

    # "Press SPACE to start" slowly blinks (between 55% and 100% bright), with a dark shadow
    brightness = 0.775 + 0.225 * math.sin(time.time() * 4)
    color = [int(c * brightness) for c in MESSAGE_TITLE_COLOR]
    center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 45)
    shadow = font.render("Press SPACE to start", True, (10, 5, 25))
    screen_surface.blit(shadow, shadow.get_rect(center=(center[0] + 2, center[1] + 2)))
    text = font.render("Press SPACE to start", True, color)
    screen_surface.blit(text, text.get_rect(center=center))

    if pygame.K_SPACE in game.keys_down:
        game.state = "MISSION"

def draw_mission_screen():
    screen_surface.fill(MISSION_BACKGROUND)

    # Who sends the mission on the left, who it is about on the right
    client_x = SCREEN_WIDTH // 4
    target_x = SCREEN_WIDTH * 3 // 4
    screen_surface.blit(client_image, client_image.get_rect(midtop=(client_x, PORTRAIT_TOP)))
    screen_surface.blit(banks_image, banks_image.get_rect(midtop=(target_x, PORTRAIT_TOP)))
    draw_label("The client: ???", CLIENT_COLOR, (client_x, LABEL_Y))
    draw_label("The target: Mr. Banks", TARGET_COLOR, (target_x, LABEL_Y))

    textes = ["INCOMING MESSAGE"," Target:   Mr. Banks, senior banker."," Mission:  Enter his dream tonight.","           Make him believe he must transfer","           1,000,000 € to account FR76 ... 0042."," Payment:  generous."," Press SPACE to accept the mission."]
    draw_message(textes, center_y=MESSAGE_Y)
    if pygame.K_SPACE in game.keys_down:
        game.state = "TRANSITION"

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
    global dungeon_start, time_lost
    # The player keeps moving while an arrow key is held down
    move_player(pygame.key.get_pressed())
    move_guards()

    if dungeon_start is None:
        dungeon_start = time.time()

    # A guard touched the Weaver: Mr. Banks sleeps less deeply, he will wake up sooner
    if guard_touches_player():
        time_lost += GUARD_PENALTY
        sounds["guard_touch"].play()
    # Whispers while a guard is close. get_num_channels() is 0 when the sound is not already
    # playing: a new whisper starts only when the last one is over (like the locked door)
    if guard_is_near() and sounds["guard_near"].get_num_channels() == 0:
        sounds["guard_near"].play()

    time_left = Dream_time - (time.time() - dungeon_start) - time_lost

    draw_level(LEVEL_1)
    # Before the fog: far away or behind a wall, the guards are hidden (it's a dream!)
    draw_guards()
    # Just after a touch the player blinks (hidden 1/10 s out of 2) while being protected
    if not (player_is_protected() and int(time.time() * 10) % 2 == 0):
        draw_player()
    # player.player_x, not "from player import player_x": that would be a copy that never moves
    draw_fog(player.player_x, player.player_y)
    if player_is_protected():
        draw_label(f"-{GUARD_PENALTY} s", (255, 0, 0), (player.player_x, player.player_y - 40))
    if time_left <= 16:
        draw_state_name(f'Time left: {int(time_left)}', color=(255, 0, 0))
    else:
        draw_state_name(f'Time left: {int(time_left)}', color=(230, 190, 90))
    if time_left <= 0:
        game.state = "WAKE_UP"

def draw_loom_screen():
    # The weaving mini-game: first the rules, then the song, then the result
    loom.judge_keys(game.keys_down)
    loom.draw_loom()
    draw_state_name("THE LOOM", color=MESSAGE_TITLE_COLOR)
    draw_label(f"Threads: {loom.threads_woven()} / {len(loom.notes)}", TEXT_COLOR,
               (loom.CLOTH.centerx, loom.CLOTH.top - 25))

    if loom.loom_start is None:
        # The rules for a few seconds, then the song starts by itself: hurry up!
        # (remember the time on the first frame, like the transition)
        if loom.rules_start is None:
            loom.rules_start = time.time()
        seconds_left = loom.RULES_DURATION - (time.time() - loom.rules_start)
        draw_message([
            "Weave the dream!",
            "When an arrow reaches the top,",
            "press the same arrow key.",
            f"Weave {loom.threads_needed()} threads to win.",
            f"Starting in {int(seconds_left) + 1}...",
        ])
        # SPACE still starts it sooner, for the players who are ready
        if seconds_left <= 0 or pygame.K_SPACE in game.keys_down:
            loom.start_loom()
        return

    if not loom.loom_finished():
        # "PERFECT", "GOOD" or "MISS" just under the loom, for a short moment
        # (nothing at the start of the song, before the first arrow is played)
        if loom.judgement != "" and loom.song_time() - loom.judgement_time < loom.JUDGEMENT_DURATION:
            color = {"PERFECT": MESSAGE_TITLE_COLOR, "GOOD": TEXT_COLOR, "MISS": TARGET_COLOR}[loom.judgement]
            draw_label(loom.judgement, color, (loom.lane_x("D") + loom.LANE_WIDTH // 2, loom.TARGET_Y + 70))
        return

    if loom.threads_woven() >= loom.threads_needed():
        draw_message([
            "The dream is woven!",
            f"You wove {loom.threads_woven()} threads out of {len(loom.notes)}.",
            "Press SPACE to see the dream.",
        ])
        if pygame.K_SPACE in game.keys_down:
            start_music()  # back to the dreamy music of the game
            game.state = "WEAVING"
    else:
        draw_message([
            "The threads broke...",
            f"Only {loom.threads_woven()} threads: you need {loom.threads_needed()}.",
            "Press SPACE to weave again.",
        ])
        if pygame.K_SPACE in game.keys_down:
            loom.reset_loom()
            loom.start_loom()

def thread_rect(direction, index, length):
    # The rectangle of a thread, from the top (vertical) or the left (horizontal) edge
    if direction == "vertical":
        return pygame.Rect(VERTICAL_THREADS[index] - THREAD_WIDTH // 2, 0, THREAD_WIDTH, length)
    return pygame.Rect(0, HORIZONTAL_THREADS[index] - THREAD_WIDTH // 2, length, THREAD_WIDTH)

def draw_thread_part(rect, color):
    # A dark border around the thread, so the threads crossing each other can be told apart
    pygame.draw.rect(screen_surface, (10, 5, 25), rect.inflate(4, 4))
    pygame.draw.rect(screen_surface, color, rect)

def draw_threads(elapsed):
    # The threads appear one by one and grow across the screen.
    # Vertical threads go top -> bottom, horizontal ones left -> right.
    lengths = {}
    for i, (direction, index) in enumerate(THREADS):
        thread_start = i * (WEAVING_DURATION - THREAD_GROW_TIME) / len(THREADS)
        grown = min(max((elapsed - thread_start) / THREAD_GROW_TIME, 0), 1)  # from 0 to 1
        screen_length = SCREEN_HEIGHT if direction == "vertical" else SCREEN_WIDTH
        lengths[(direction, index)] = int(grown * screen_length)

    # All the vertical threads, then the horizontal ones on top of them...
    for direction in ["vertical", "horizontal"]:
        for (thread_direction, index), length in lengths.items():
            if thread_direction == direction and length > 0:
                color = THREAD_COLORS[(index + (direction == "horizontal")) % len(THREAD_COLORS)]
                draw_thread_part(thread_rect(direction, index, length), color)

    # ...then at one crossing out of two, the vertical thread goes back on top:
    # over, under, over, under... that is what makes it look woven
    for column, x in enumerate(VERTICAL_THREADS):
        for row, y in enumerate(HORIZONTAL_THREADS):
            vertical_reaches = lengths[("vertical", column)] > y + THREAD_WIDTH
            horizontal_reaches = lengths[("horizontal", row)] > x + THREAD_WIDTH
            if (column + row) % 2 == 0 and vertical_reaches and horizontal_reaches:
                crossing = pygame.Rect(0, 0, THREAD_WIDTH, THREAD_WIDTH + 8)
                crossing.center = (x, y)
                draw_thread_part(crossing, THREAD_COLORS[column % len(THREAD_COLORS)])

def draw_weaving_screen():
    global weaving_start
    global THE_VICTORY_NUMBER
    # Remember the time on the first frame of the weaving
    # (not when coming back from the DEMO screen: the threads are already woven)
    if weaving_start is None:
        weaving_start = time.time()
    elapsed = time.time() - weaving_start
    weaving_done = elapsed >= WEAVING_DURATION

    screen_surface.fill((20, 90, 90))
    draw_threads(elapsed)
    draw_state_name("WEAVING", color=(192, 242, 57))

    if not weaving_done:
        draw_message(["Weaving the dream..."], center_y=SCREEN_HEIGHT - 60)
        return  # the choice is shown once all the threads are woven

    textes = ["Chose the weath-in threds "," [1]   Transfer to the acount thread"," [2]   Keep the money and try to find who did this thread"," [3]   Do nothing and leave the dream","Chose a number."]
    draw_message(textes)
    if pygame.K_1 in game.keys_down:
        THE_VICTORY_NUMBER = 1
        game.state = "WIN"
    elif pygame.K_2 in game.keys_down:
        THE_VICTORY_NUMBER = 2
        game.state = "WIN"
    elif pygame.K_3 in game.keys_down:
        THE_VICTORY_NUMBER = 3
        game.state = "WIN"

def draw_wake_up_screen():
    screen_surface.blit(wake_up_image, (0, 0))
    draw_message([
        "Mr. Banks woke up!",
        "You were thrown out of his dream.",
        "Press SPACE to try again."
    ], center_y=WIN_MESSAGE_Y)
    if pygame.K_SPACE in game.keys_down:
        reset_game()
        game.state = "MISSION"

def draw_win_screen():
    global THE_VICTORY_NUMBER
    if THE_VICTORY_NUMBER == 1:
        screen_surface.blit(win_image1, (0, 0))
        draw_message([
            "Mission complete.",
            "Mr. Banks made a very generous transfer...",
            "Press SPACE to play again.",
        ], center_y=WIN_MESSAGE_Y)
        if pygame.K_SPACE in game.keys_down:
            reset_game()
            game.state = "MISSION"
    elif THE_VICTORY_NUMBER == 2:
        screen_surface.blit(win_image2, (0, 0))
        draw_message([
            "When Mr. Banks found out...",
            "that someone tried to steal his money.",
            "he started searching the thief",
            "Press SPACE to play again.",
        ], center_y=WIN_MESSAGE_Y)
        if pygame.K_SPACE in game.keys_down:
            reset_game()
            game.state = "MISSION"
    elif THE_VICTORY_NUMBER == 3:
        screen_surface.blit(win_image3, (0, 0))
        draw_message([
            "You didn't do what he asked you.",
            "but he gives you another chance to be pardoned.",
            "Press SPACE to play again.",
        ], center_y=WIN_MESSAGE_Y)
        if pygame.K_SPACE in game.keys_down:
            reset_game()
            game.state = "MISSION"

def draw_demo_screen():
    screen_surface.fill((20, 90, 90))
    draw_state_name("DEMO", color=(242, 52, 119))
    textes = ["Sorry you are in the demo ","buy the full game","to chose this way","if you bought it call this number: 1-800-123-4567","if you want to countinue the demo press SPACE to go back to the weaving screen"]
    draw_message(textes)
    if pygame.K_SPACE in game.keys_down:
        game.state = "WEAVING"