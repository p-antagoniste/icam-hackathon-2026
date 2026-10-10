# The Dream Weaver: Development Plan

> Hackathon theme: *weaving patterns, weaving ideas, weaving communities*

## 1. The game in one paragraph

You play **the Dream Weaver**, a mysterious specialist who takes missions from anonymous clients.
Nobody knows if those clients are good or evil. The Weaver can slip into a sleeping person's mind
(like in *Inception*) and weave a dream there that changes what the person does when they wake up.

**Mission 1:** get into the mind of a **banker** and weave a dream that makes him transfer a large
sum of money to a specific account.

## 2. Golden rule: always have something that works

1. Build the **smallest playable version** first (the MVP, minimum viable product).
2. **Commit to git after every step** so there is always a working version to show.
3. Add bonus features one at a time. If one breaks the game and you can't fix it quickly, go back
   to the last commit (`git checkout .`).

If time runs out after step 7, you still have a complete game with a start, a middle and an end.

## 3. Technical choices (kept simple)

| Topic | Choice | Why |
|---|---|---|
| Language / library | Python + **pygame-ce** (already installed in `.venv`) | Already working in `main.py` |
| Screen | 800 × 600 (already set) | |
| Grid | **Tiles of 40 × 40 px**, so 20 columns × 15 rows | The player sprites (`grafiki/player/`) are 40 × 40 |
| Map | A **list of strings**, one letter per tile | Edit the level in a text editor, no tools needed |
| Movement | **One key press = one tile** | Wall collisions become very easy (check the target tile) |
| Code layout | Keep a single `main.py` for now | Easy to read. Split it later only if it gets long |
| Graphics | Coloured rectangles first, images later | Gameplay first, art second |

## 4. The core idea: game "states"

The game is always on exactly **one screen** (a *state*). The main loop checks the current state
and runs the matching code:

```
 MISSION  --SPACE-->  TRANSITION  --(3 sec)-->  DUNGEON  --reach door with key-->  WEAVING  --(3 sec)-->  WIN
    ^                                                                                                     |
    +----------------------------------------- SPACE (play again) ---------------------------------------+
```

```python
state = "MISSION"

while running:
    for event in pygame.event.get():
        ...  # handle keys depending on state

    if state == "MISSION":
        draw_mission_screen()
    elif state == "TRANSITION":
        draw_transition_screen()
    elif state == "DUNGEON":
        update_and_draw_dungeon()
    elif state == "WEAVING":
        draw_weaving_screen()
    elif state == "WIN":
        draw_win_screen()
```

This is the backbone of the whole game. Build it first.

---

## 5. MVP: step by step

Each step ends with a **"Done when…"** check. Don't move on until it passes, then commit.

### Step 0: Clean-up (≈ 10 min)
- Rename the window caption to `"The Dream Weaver"`.
- Remove the unused parts of `main.py` (score, `random`, the commented `screns_play` block).
- Add a `requirements.txt` containing `pygame-ce`.

**Done when:** the game starts with the new title and the player still moves.

### Step 1: State machine skeleton (≈ 30 min)
- Add the `state` variable and the `if/elif` block shown above.
- Each state just fills the screen with a different colour and shows its name as text.
- SPACE moves to the next state (temporarily, to test).

**Done when:** pressing SPACE cycles MISSION → TRANSITION → DUNGEON → WEAVING → WIN → MISSION.

### Step 2: Mission screen (≈ 30 min)
- Dark background, title "The Dream Weaver".
- A short mission message, shown line by line (one `font.render` per line):

  ```
  INCOMING MESSAGE (sender: unknown)

  Target:   Mr. Banks, senior banker.
  Mission:  Enter his dream tonight.
            Make him believe he must transfer
            1,000,000 € to account FR76 ... 0042.
  Payment:  generous.

  Press SPACE to accept the mission.
  ```

**Done when:** the mission is readable and SPACE starts the transition.

### Step 3: Transition screen, "entering the mind" (≈ 30 min)
Simple, cheap effect: a **spiral or circle that grows** from the centre of the screen for
~3 seconds, with the text "Entering the dream of Mr. Banks…".

- Remember the time when entering the state: `transition_start = time.time()`
- Each frame: `progress = (time.time() - transition_start) / 3`
- Draw a circle with radius `progress * 500` (`pygame.draw.circle`)
- When `progress >= 1`, set `state = "DUNGEON"`

**Done when:** the effect plays and the dungeon starts by itself.

### Step 4: Draw the dungeon from a map (≈ 45 min)
Each letter is a 40 × 40 tile: `W` = wall, `.` = floor, `P` = player start, `K` = key, `D` = door.

```python
LEVEL_1 = [
    "WWWWWWWWWWWWWWWWWWWW",
    "WP.....W...........W",
    "W.WWWW.W.WWWWWWWWW.W",
    "W.W....W.........W.W",
    "W.W.WWWWWWWWWWWW.W.W",
    "W.W......W.....W.W.W",
    "W.WWWWWW.W.WWW.W.W.W",
    "W......W.W..KW.W...W",
    "WWWWWW.W.WWWWW.WWWWW",
    "W......W.......W...W",
    "W.WWWWWWWWWWWW.W.W.W",
    "W..............W.W.W",
    "WWWWWWWWWWWWW.WW.W.W",
    "W................W.D",
    "WWWWWWWWWWWWWWWWWWWW",
]
```
(This map has been checked: 20 × 15 tiles, and both the key and the door can be reached.)

- Loop over rows (`y`) and columns (`x`), draw a rectangle at `(x * 40, y * 40)`.
- Colours for now: walls dark purple, floor dark blue, key yellow, door brown.
- Read the player start position from the `P` tile.

**Done when:** the maze appears on screen.

### Step 5: Grid movement and walls (≈ 45 min)
- Store the player position **in tiles** (`player_x`, `player_y`), not in pixels.
- On a `KEYDOWN` event (not `get_pressed`, which moves too fast), compute the target tile.
- Move only if the target tile is **not** `W`.
- Draw the player at `(player_x * 40, player_y * 40)`. Show the player sprite facing the last move direction (`grafiki/player/north.png`, etc.).

**Done when:** the player walks through the corridors and can't go through walls.

### Step 6: Key and locked door (≈ 30 min)
- `has_key = False`
- If the player steps on `K`, set `has_key = True` and stop drawing the key.
- The door `D` counts as a wall while `has_key` is `False`.
- Small HUD at the top: `Key: none` / `Key: found!`
- Bonus message if the player bumps into the door without the key: "Locked… I need a key."

**Done when:** you can't open the door without the key, and you can with it.

### Step 7: Weave the dream and win (≈ 30 min)
- Stepping on the door with the key switches to `WEAVING`.
- **WEAVING screen** (~3 sec): coloured lines crossing each other appear one by one (horizontal
  and vertical "threads" = a weaving pattern) with the text "Weaving the dream…".
- **WIN screen:** "Mission complete. Tomorrow morning, Mr. Banks will make a very generous
  transfer…" + "Press SPACE to play again".
- Restarting must reset everything (`has_key`, player position, key visible again).

**Done when:** you can play the full game from start to end, twice in a row.

### 🎉 MVP finished (≈ 4–5 h in total)
Commit and tag it: `git tag mvp`. That is your safe version for the demo.

---

## 6. Improvements (only if there is time)

Ordered from **best effect for least effort** to **more ambitious**. Pick in order and commit
after each one.

| # | Improvement | Effort | Idea |
|---|---|---|---|
| A | **Real graphics** | ★☆☆ | 40 × 40 PNGs for wall, floor, key, door, drawn by hand (Piskel, or paper + photo). Load them with `load_sprite` like the player |
| B | **Fog of war** | ★☆☆ | Dreams are blurry: draw a black layer over the screen with a transparent circle around the player. Looks great, about 10 lines of code |
| C | **Timer** | ★☆☆ | "Mr. Banks wakes up in 60 s." If time runs out you're thrown out of the dream (game over → restart) |
| D | **Sound** | ★☆☆ | Dreamy background music + sounds for "key picked up" and "door opened" (`pygame.mixer`) |
| E | **Memory fragments** | ★★☆ | Use the existing `bonus_1..3.png`: collect 3 "threads" before the door opens |
| F | **Guards (projections)** | ★★☆ | As in *Inception*, the mind defends itself: enemies walk back and forth along a corridor. Touching one wakes the banker up → restart |
| G | **Weaving mini-game** | ★★☆ | At the door, press a sequence of arrows shown on screen (↑ → ↓ ←…) to weave the threads. Each correct key adds a coloured thread |
| H | **Level 2 / dream layers** | ★★☆ | A second map = "a deeper dream". Easy once levels are lists of strings: `LEVELS = [LEVEL_1, LEVEL_2]` |
| I | **Moral choice + 2 endings** | ★★☆ | At the door: "Weave the ordered dream" or "Weave a warning dream". One ending reveals the client was a thief, the other that the banker was the criminal… |
| J | **Smooth movement / animation** | ★★★ | Slide between tiles, 2-frame walking animation |

**Recommended order if you have half a day more:** A → B → G → I. They show the theme best for the
least code.

---

## 7. Linking the game to the theme (for the pitch)

- **Weaving patterns:** the maze is a pattern of corridors, and the final act is literally weaving
  threads together (WEAVING screen / mini-game G).
- **Weaving ideas:** the Weaver plants an idea in someone's mind. Ideas are threads woven into a
  dream.
- **Weaving communities:** every mission connects strangers (anonymous client, Weaver, victim)
  without them knowing each other. Ending I can show that one woven dream changes a whole community.

## 8. Who does what (suggestion)

| Son | Dad |
|---|---|
| Draws the sprites (player, wall, key, door) | Writes the state machine (step 1) |
| Designs the maze on squared paper, then types it as strings | Map drawing + movement (steps 4–5) |
| Writes the mission and ending texts | Key/door logic (step 6) |
| Plays and tests every step ("Done when…") | Commit after each step |

Switch roles sometimes: steps 2, 3 and 6 are good ones for the son to code.

## 9. Demo checklist

- [ ] The game starts with `.venv/bin/python main.py` with no errors
- [ ] Full run (mission → dream → key → door → win) works twice in a row
- [ ] The `mvp` tag exists in git
- [ ] A 30-second pitch is ready (story + theme link, section 7)
- [ ] A backup screen recording of a full run, in case something goes wrong live
