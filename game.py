# ---------------- STATES ----------------
# The game is always on exactly one of these screens, in this order
STATES = ["TITLE", "MISSION", "TRANSITION", "DUNGEON", "LOOM", "WEAVING", "WAKE_UP", "WIN"]

# The current screen. Other files change it with game.state = "..."
# Always write "import game" then game.state: "from game import state" would make a copy
# that never sees the changes
state = "TITLE"

def next_state(current_state):
    # After the last state, go back to the first one
    index = STATES.index(current_state)
    return STATES[(index + 1) % len(STATES)]

# The keys pressed during this frame, filled by main.py from the KEYDOWN events.
# Unlike pygame.key.get_pressed(), a key held down only counts once: the SPACE that
# leaves the WIN screen doesn't also skip the MISSION screen
keys_down = []
