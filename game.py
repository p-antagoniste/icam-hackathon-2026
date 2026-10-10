# ---------------- STATES ----------------
# The game is always on exactly one of these screens, in this order
STATES = ["MISSION", "TRANSITION", "DUNGEON", "WEAVING", "WIN"]

# The current screen. Other files change it with game.state = "..."
# Always write "import game" then game.state: "from game import state" would make a copy
# that never sees the changes
state = "MISSION"

def next_state(current_state):
    # After the last state, go back to the first one
    index = STATES.index(current_state)
    return STATES[(index + 1) % len(STATES)]
