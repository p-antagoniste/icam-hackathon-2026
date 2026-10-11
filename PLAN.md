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
| Screen | 800 × 720 (already set) | |
| Grid | **Tiles of 40 × 40 px**, so 20 columns × 18 rows | The player sprites (`grafiki/player/`) are 40 × 40 |
| Map | A **list of strings**, one letter per tile | Edit the level in a text editor, no tools needed |
| Movement | **Smooth, in pixels, while the key is held** | Walls are checked with a small hitbox against the `W` tiles |
| Code layout | Small files of about 100 lines (`main.py` is the game loop, the list of files is at its top) | Easy to read: each file does one job |
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

### Step 5: Smooth movement and walls (≈ 45 min)
- Store the player position **in pixels** (`player_x`, `player_y` = the centre of the player),
  starting in the middle of the `P` tile.
- Each frame, read the held keys with `pygame.key.get_pressed()`: the player keeps moving while
  an arrow key is held (`PLAYER_SPEED` = 3 pixels per frame).
- Walls: a **hitbox** of 28 × 28 px (a bit smaller than a tile, so corridors are easy) must never
  touch a `W` tile. Checking its 4 corners is enough: `LEVEL_1[y // 40][x // 40]`.
- Move one pixel at a time, x and y separately: the player stops right against a wall and slides
  along it.
- Draw the player sprite centred on `(player_x, player_y)`, facing the last move direction
  (`grafiki/player/north.png`, etc.).

**Done when:** the player walks through the corridors and can't go through walls.

### Step 6: Key and locked door (≈ 30 min)
- `has_key = False`
- If the tile under the player's centre (`player_x // 40`, `player_y // 40`) is `K`, set
  `has_key = True` and stop drawing the key.
- The door `D` counts as a wall while `has_key` is `False` (in `hits_wall`).
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
| E | **Memory fragments** | ★★☆ | Use the 3 thread spools (`grafiki/objects/thread_*.png`): collect 3 "threads" before the door opens |
| F | **Guards (projections)** | ★★☆ | As in *Inception*, the mind defends itself: enemies walk back and forth along a corridor. Touching one wakes the banker up → restart |
| G | **Weaving mini-game** | ★★☆ | At the door, press a sequence of arrows shown on screen (↑ → ↓ ←…) to weave the threads. Each correct key adds a coloured thread |
| H | **Level 2 / dream layers** | ★★☆ | A second map = "a deeper dream". Easy once levels are lists of strings: `LEVELS = [LEVEL_1, LEVEL_2]` |
| I | **Moral choice + 2 endings** | ★★☆ | At the door: "Weave the ordered dream" or "Weave a warning dream". One ending reveals the client was a thief, the other that the banker was the criminal… |
| J | **Walking animation** | ★★★ | 2-frame walking animation per direction (movement is already smooth) |

**Recommended order if you have half a day more:** A → B → G → I. They show the theme best for the
least code.

### Improvement C: Timer, step by step

The goal: when the dungeon starts, a countdown starts too. "Mr. Banks wakes up in 60 s". If it
reaches 0 before the door is opened, the player is thrown out of the dream and has to start again.

You already know the trick, because the TRANSITION screen uses it: remember the start time on
the first frame, then compute how much time has passed. Look at `draw_transition_screen()` in
`screens.py` before you start.

Same as the MVP: don't move on before **"Done when…"** passes, and commit after each step.

#### C1: Start the clock when the dungeon starts (≈ 10 min)
- In `screens.py`, near the other constants at the top, add a new section with:
  - `DREAM_DURATION = 60` (seconds before Mr. Banks wakes up)
  - `dungeon_start = None` (set on the first frame of the dungeon)
- In `update_and_draw_dungeon()`, do like `transition_start`: if `dungeon_start` is `None`, set
  it to `time.time()`. Don't forget the `global dungeon_start` line at the top of the function,
  or Python makes a new local variable instead of changing the one at the top of the file.
- Compute the time left: `time_left = DREAM_DURATION - (time.time() - dungeon_start)`.
- To check it, `print(time_left)` (the numbers show in the terminal, not in the game).

**Done when:** the terminal shows numbers going down from 60 while you walk in the dungeon.
Remove the `print` afterwards.

#### C2: Show the countdown on screen (≈ 15 min)
- At the **end** of `update_and_draw_dungeon()`, **after** `draw_fog(...)`, draw the text
  `"Mr. Banks wakes up in 42 s"`. If you draw it before the fog, the fog hides it!
- `int(time_left)` turns `42.738` into `42`.
- The easiest way: `draw_state_name("...")` already draws a text with a shadow at the top of the
  screen. Or copy what it does with `font.render(...)` if you want to choose the position.

**Done when:** the countdown is readable at the top of the dungeon and goes down every second.

#### C3: Make it scary at the end (≈ 15 min)
- When `time_left` is below 10 s, draw the text in red instead of white.
- Bonus: make it blink. The title screen already does that with
  `math.sin(time.time() * 4)` (look at `draw_title_screen()`).
- Add a constant for it at the top: `HURRY_TIME = 10`.

**Done when:** the last 10 seconds are red (and blink, if you did the bonus).

#### C4: The "wake up" screen (≈ 30 min)
A new screen, so follow the 4 steps from `CLAUDE.md` (section *Architecture*):
1. Add `"WAKE_UP"` at the end of `STATES` in `game.py`.
2. In `screens.py`, write `draw_wake_up_screen()`, like `draw_win_screen()`: a background
   colour, `draw_state_name("WAKE UP")` and a `draw_message([...])`, for example:
   ```
   Mr. Banks woke up!
   You were thrown out of his dream.
   Press SPACE to try again.
   ```
   (remember: the first line is the gold title and the last one blinks).
   When SPACE is pressed: call `reset_game()`, then `game.state = "MISSION"`.
3. In `main.py`, import `draw_wake_up_screen` and add an `elif game.state == "WAKE_UP":` branch.
4. In `update_and_draw_dungeon()`: when `time_left <= 0`, set `game.state = "WAKE_UP"`.

**Done when:** waiting 60 s in the dungeon shows the wake up screen.
**Testing tip:** put `DREAM_DURATION = 5` while testing so you don't wait a whole minute each
time. Put it back to 60 at the end!

#### C5: Restart with a full timer (≈ 10 min)
Try this: lose once, press SPACE, go back into the dungeon. Is the timer at 60 again? Probably
not, because `dungeon_start` still holds the time of the **first** game.

- In `reset_game()` (in `screens.py`), set `dungeon_start = None`, like `weaving_start`
  (add it to the `global` line).
- `reset_game()` is called both after the WIN screen and after the WAKE_UP screen, so this fixes
  both ways of finishing a game.

**Done when:** you can lose, play again, win, play again: every time the timer starts at 60.

#### C6: Polish (optional, pick what you like)
- **Sound:** make an alarm clock sound with ElevenLabs, save it as `sound/wake_up.mp3`, add it to
  `sounds` in `assets.py` and to `SCREEN_SOUNDS` with `"WAKE_UP": "wake_up"`. It then plays by
  itself when the screen starts.
- **Score:** remember the time left when the door opens and show it on the WIN screen:
  "Mission complete with 23 s to spare!"
- **Balance:** play it several times and pick the right `DREAM_DURATION`: hard, but not
  impossible on the first try.

**Done when:** the full game works twice in a row (win once, lose once), then commit:
`feat: add the dream timer`.

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
