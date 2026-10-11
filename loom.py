import time
import pygame

from window import screen_surface, SCREEN_HEIGHT
from assets import sounds, start_music

# ---------------- LOOM ----------------
# The weaving mini-game, like Dance Dance Revolution: arrows climb up the screen, and the
# same arrow key must be pressed when an arrow reaches the loom at the top.
# Each good key weaves one coloured thread into the cloth on the right.

LOOM_MUSIC = "loom_song.mp3"  # made with Suno, in the music folder
LOOM_BPM = 100            # beats per minute of the music (Suno was asked for 100 BPM)
STEPS_PER_BEAT = 2        # each letter of the song lasts half a beat
MUSIC_START = 0.13        # seconds before the first beat of the music (measured with ffmpeg)
SCROLL_SPEED = 300        # pixels per second: how fast the arrows climb
PERFECT_WINDOW = 0.07     # seconds too early or too late that still count as "PERFECT"
GOOD_WINDOW = 0.16        # ... and as "GOOD". Later than that, the thread is missed
PASS_PERCENT = 60         # how many threads (in %) must be woven for the dream to hold
FLASH_DURATION = 0.15     # seconds the grey arrow lights up after a good key
JUDGEMENT_DURATION = 0.4  # seconds "PERFECT", "GOOD" or "MISS" stays on the screen
END_PAUSE = 1             # seconds between the last arrow and the result

# The song: one letter per half beat. L left, D down, U up, R right, "." nothing.
# Change it to make your own dance! (the lines are joined into one long text)
# Each line is 8 beats of the music (4.8 s). The 1st, 3rd, 5th... letters fall on a beat,
# the others between two beats. The start of each group of 4 ("L...") is a big drum.
SONG = (
    "........L...R..."  # beats 0-8: the soft start of the music
    "L...D...U...R..."  # beats 8-16: the drums start
    "L.R.L.R.U.D.U.D."  # beats 16-24
    "L.D.U.R.R.U.D.L."  # beats 24-32: the music gets loud
    "LR..UD..LU..RD.."  # beats 32-40
    "L.L.R.R.U.U.D.D."  # beats 40-48
    "LDUR.RUDL...L..."  # beats 48-56: the end of the music
)

# The 4 lanes, in the order of Dance Dance Revolution: left, down, up, right
LANES = ["L", "D", "U", "R"]
LANE_KEYS = {"L": pygame.K_LEFT, "D": pygame.K_DOWN, "U": pygame.K_UP, "R": pygame.K_RIGHT}
# Gold, cyan, red and purple, like the threads of the WEAVING screen
LANE_COLORS = {"L": (230, 190, 90), "D": (80, 200, 255), "U": (220, 70, 90), "R": (150, 90, 220)}
LANE_WIDTH = 80
LANES_LEFT = 60      # x of the left side of the first lane
TARGET_Y = 140       # the loom: where an arrow must be when its key is pressed
ARROW_SIZE = 28      # pixels from the middle of an arrow to its tip
BACKGROUND = (15, 10, 30)
DARK = (10, 5, 25)   # outlines

# The cloth on the right: it grows from the bottom, one row per thread of the song
CLOTH = pygame.Rect(440, 110, 320, 560)
WARP_SPACING = 20    # pixels between two vertical threads of the loom
WARP_COLOR = (70, 60, 100)

# One dictionary per arrow of the song, made by reset_loom()
notes = []
loom_start = None   # when the song started (None = not started yet)
judgement = ""      # the last "PERFECT", "GOOD" or "MISS", shown under the loom
judgement_time = 0  # when it happened (in seconds of the song)
lane_flash = {}     # lane -> when its last good key was pressed

# ---------------- FUNCTIONS ----------------

def reset_loom():
    # The song back to the start, with no thread woven yet
    global loom_start, judgement
    loom_start = None
    judgement = ""
    lane_flash.clear()
    notes.clear()
    step_duration = 60 / LOOM_BPM / STEPS_PER_BEAT  # seconds between two letters
    for step, letter in enumerate(SONG):
        if letter in LANES:
            notes.append({"lane": letter, "time": MUSIC_START + step * step_duration, "result": None})

reset_loom()

def start_loom():
    # The music and the arrows start at the same time
    global loom_start
    start_music(LOOM_MUSIC, loops=0)  # only once: the dance ends with the music
    loom_start = time.time()

def song_time():
    # Seconds since the song started (0 before it starts)
    if loom_start is None:
        return 0
    return time.time() - loom_start

def judge_keys(keys_down):
    # Check the keys pressed this frame, and the arrows that went past without a key
    global judgement, judgement_time
    now = song_time()
    for lane in LANES:
        if LANE_KEYS[lane] in keys_down:
            # The first arrow of this lane that is close enough to the loom
            for note in notes:
                gap = abs(note["time"] - now)
                if note["lane"] == lane and note["result"] is None and gap <= GOOD_WINDOW:
                    note["result"] = "PERFECT" if gap <= PERFECT_WINDOW else "GOOD"
                    judgement, judgement_time = note["result"], now
                    lane_flash[lane] = now
                    sounds["loom_hit"].play()
                    break
    for note in notes:
        if note["result"] is None and now - note["time"] > GOOD_WINDOW:
            note["result"] = "MISS"
            judgement, judgement_time = "MISS", now
            sounds["loom_miss"].play()

def threads_woven():
    return len([note for note in notes if note["result"] in ("PERFECT", "GOOD")])

def threads_needed():
    # PASS_PERCENT of the threads, rounded up
    return -(-len(notes) * PASS_PERCENT // 100)

def loom_finished():
    return song_time() > notes[-1]["time"] + GOOD_WINDOW + END_PAUSE

def arrow_points(center, lane):
    # An arrow pointing up, made of 7 points around its middle (0, 0)...
    s = ARROW_SIZE
    points = [(0, -s), (s, 0), (s // 3, 0), (s // 3, s), (-s // 3, s), (-s // 3, 0), (-s, 0)]
    # ...then turned to point the right way
    if lane == "D":
        points = [(x, -y) for x, y in points]
    elif lane == "L":
        points = [(y, x) for x, y in points]
    elif lane == "R":
        points = [(-y, x) for x, y in points]
    return [(center[0] + x, center[1] + y) for x, y in points]

def draw_arrow(center, lane, color):
    points = arrow_points(center, lane)
    pygame.draw.polygon(screen_surface, color, points)
    pygame.draw.polygon(screen_surface, DARK, points, 3)

def lane_x(lane):
    # The x of the middle of a lane
    return LANES_LEFT + LANES.index(lane) * LANE_WIDTH + LANE_WIDTH // 2

def draw_cloth():
    # The vertical threads of the loom (the "warp"), always there
    pygame.draw.rect(screen_surface, DARK, CLOTH.inflate(8, 8))
    warp_xs = list(range(CLOTH.left + WARP_SPACING // 2, CLOTH.right, WARP_SPACING))
    for x in warp_xs:
        pygame.draw.line(screen_surface, WARP_COLOR, (x, CLOTH.top), (x, CLOTH.bottom), 4)

    # One horizontal thread per good key, from the bottom up. A missed key leaves a hole
    row_height = CLOTH.height // len(notes)
    for row, note in enumerate(notes):
        if note["result"] not in ("PERFECT", "GOOD"):
            continue
        y = CLOTH.bottom - (row + 1) * row_height
        pygame.draw.rect(screen_surface, LANE_COLORS[note["lane"]], (CLOTH.left, y, CLOTH.width, row_height - 2))
        # Over, under, over, under: one warp thread out of two goes back on top
        for column, x in enumerate(warp_xs):
            if (column + row) % 2 == 0:
                pygame.draw.line(screen_surface, WARP_COLOR, (x, y), (x, y + row_height - 2), 4)

def draw_loom():
    screen_surface.fill(BACKGROUND)
    now = song_time()
    held = pygame.key.get_pressed()

    for lane in LANES:
        # A faint band for each lane, and the grey arrow of the loom at the top.
        # It lights up when its key is held, and in colour just after a good key
        band = pygame.Rect(lane_x(lane) - LANE_WIDTH // 2 + 4, 0, LANE_WIDTH - 8, SCREEN_HEIGHT)
        pygame.draw.rect(screen_surface, (25, 18, 45), band)
        target_color = (120, 110, 140) if held[LANE_KEYS[lane]] else (70, 60, 90)
        if lane in lane_flash and now - lane_flash[lane] < FLASH_DURATION:
            target_color = LANE_COLORS[lane]
        draw_arrow((lane_x(lane), TARGET_Y), lane, target_color)

    # The arrows still to play climb up towards the loom
    for note in notes:
        y = TARGET_Y + (note["time"] - now) * SCROLL_SPEED
        if note["result"] is None and y < SCREEN_HEIGHT + ARROW_SIZE:
            draw_arrow((lane_x(note["lane"]), int(y)), note["lane"], LANE_COLORS[note["lane"]])

    draw_cloth()
