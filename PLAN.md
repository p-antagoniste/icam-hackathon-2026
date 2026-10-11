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
| F | **Guards (projections)** | ★★☆ | As in *Inception*, the mind defends itself: enemies walk back and forth along a corridor. Touching one costs 20 s: the banker wakes up sooner |
| G | **Weaving mini-game** | ★★☆ | At the door, press a sequence of arrows shown on screen (↑ → ↓ ←…) to weave the threads. Each correct key adds a coloured thread |
| H | **Level 2 / dream layers** | ★★☆ | A second map = "a deeper dream". Easy once levels are lists of strings: `LEVELS = [LEVEL_1, LEVEL_2]` (step by step below) |
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

### Improvement F: Guards (projections), step by step

The goal: like in *Inception*, Mr. Banks's mind defends itself. **3 guards** (dream
"projections") walk back and forth, always on the same line. If one touches the Weaver, it's
not game over: Mr. Banks sleeps less deeply and **20 seconds disappear from the timer**. The
game only ends when the timer reaches 0 (the WAKE_UP screen from improvement C), so 3 touches
in a 60 s dream is already too many.

Level 1 must stay easy, so the guards are **slow, never chase you, and never leave their line**.
The trick is to wait for the right moment, hidden in a side passage. Or to rush through a guard
when you have time to spare!

#### F0: What to create first (PixelLab and ElevenLabs)

Start the pictures and sounds now: they're made while you code F1 to F3 with red squares
(golden rule: coloured rectangles first, images later).

**Character in PixelLab: the guard.** Use the same settings as the player (40 × 40, top-down
view, 4 directions, same outline and shading), so the guard fits with the player and the tiles.

- **Prompt:**
  ```
  A dream projection guard: a tall faceless man in a dark charcoal grey business suit, white
  shirt and dark red tie, smooth pale grey face with no mouth and no nose, only two small
  glowing red eyes, a faint purple ghostly glow around his outline, arms stiff along his body.
  Like a bank security agent seen in a dream: creepy but not scary for kids, no weapon, no blood.
  Pixel art, top-down RPG character, dark dreamy colours (purple, grey, red).
  ```
- **Animation:** the *walking* animation in the 4 directions, with this description:
  ```
  A slow, stiff, robotic walk, like a sleepwalker on patrol.
  ```
- **Files to save** in a new folder `grafiki/guard/`, with the same names as the player:
  `south.png`, `north.png`, `east.png`, `west.png` and `walking_south.gif`, `walking_north.gif`,
  `walking_east.gif`, `walking_west.gif`. (The 3 guards of level 1 only walk left and right,
  so `east` and `west` are the most important.)

No new object is needed: the guards are the only new pictures.

**Sounds in ElevenLabs (Sound Effects).** Save them in `sound/` with these names:

| File | When | Length | Prompt |
|---|---|---|---|
| `guard_touch.mp3` | a guard touches the Weaver: 20 s are lost | ~1.5 s | `A sudden dreamlike jolt: a sharp reversed whoosh, then an old clock ticking very fast as if time jumps forward, ending with one deep heartbeat thump. Eerie, cinematic, reverb, no music.` |
| `guard_near.mp3` (bonus, F5) | a guard is close | ~2 s | `Low eerie whispers of several distant voices murmuring words you can't understand. Ghostly, soft, dreamlike reverb, no music.` |

The touch is not the end of the game: the sound plays while you keep walking, so it must be short
and must not sound like the alarm clock (`wake_up.mp3` is kept for when Mr. Banks really wakes up).
It should sound like *"time just jumped forward"*.

#### Where the guards walk

Each number shows the tiles one guard walks on, back and forth:

```
           0         1
           01234567890123456789
   row  0  WWWWWWWWWWWWWWWWWWWW
   row  1  WP..W...........W..W
   row  2  W...W.111111111.W..W
   row  3  W...W..WWWWWWW..W..W
   row  4  W...W........W.....W
   row  5  W............W.....W
   row  6  W.........WWWWWW...W
   row  7  W.........W........W
   row  8  WWWWWW....W........W
   row  9  W.KW......W...WWWWWW
   row 10  W..W......W22222222W
   row 11  W..W...WWWW22222222W
   row 12  W..W...W.......W...W
   row 13  W..W...W.......W.D.W
   row 14  W..WWWWW.......WWWWW
   row 15  W...333333333333...W
   row 16  W...333333333333...W
   row 17  WWWWWWWWWWWWWWWWWWWW
```

| Guard | Route (column, row) | Why it is there | How to get past |
|---|---|---|---|
| 1 | (6, 2) → (14, 2) | The top corridor, the only way to the right side. The **easy** one, to learn how guards move | It walks on row 2 only: sneak past on row 1, against the top wall |
| 2 | (11, 10.5) → (18, 10.5) | The big room before the door | It blocks both rows: wait in row 9 (or row 12) and cross when it's far away |
| 3 | (4, 15.5) → (15, 15.5) | The bottom corridor, on the way to the key (crossed twice) | It blocks both rows: wait in the opening above (row 14) or in the key corridor, then go |

**Why 10.5 and 15.5?** A guard in the middle of a tile only blocks one row, and a corridor 2 tiles
wide has room to pass next to it. Row 10.5 means *"between row 10 and row 11"*: the guard walks on
the line between the two rows and blocks the whole corridor. The side passages are always out of
reach, so there's always a safe place to wait. In a hurry, you can also walk straight through a
guard: it costs 20 s.

Same as the MVP: don't move on before **"Done when…"** passes, and commit after each step.

#### F1: One guard, as a red square (≈ 30 min)
- Create a new file `guards.py`, and add it to the list of files at the top of `main.py`.
- Constants at the top:
  - `GUARD_SPEED = 2` (pixels per frame: slower than the player, who does 3)
  - `GUARD_HITBOX_SIZE = 28` (the same as the player)
  - `GUARD_COLOR = (220, 70, 90)` (red, until the PixelLab picture is ready)
  - `GUARD_ROUTES`, only the first guard for now: `[((6, 2), (14, 2))]`
- A guard is a **dictionary**: its position in pixels, the two ends of its route, and where it
  is going. `guards = []` holds them all.
- `tile_center(column, row)` gives the pixels of the middle of a tile:
  `(column * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)`.
- `reset_guards()` puts every guard back at the start of its route (call it once at the bottom
  of the file, like `reset_player()` in `player.py`):
  ```python
  guards.clear()
  for start, end in GUARD_ROUTES:
      x, y = tile_center(*start)
      guards.append({"x": x, "y": y, "start": tile_center(*start), "end": tile_center(*end),
                     "going_to_end": True, "direction": "east"})
  ```
- `move_guards()` moves each guard one step towards the end it is going to:
  ```python
  for guard in guards:
      if guard["going_to_end"]:
          target_x, target_y = guard["end"]
      else:
          target_x, target_y = guard["start"]
      # Arrived (or less than one step left): stand on the end and turn around
      if abs(target_x - guard["x"]) + abs(target_y - guard["y"]) <= GUARD_SPEED:
          guard["x"], guard["y"] = target_x, target_y
          guard["going_to_end"] = not guard["going_to_end"]
      # Otherwise one step towards it (a route is a straight line: only x or only y changes)
      elif target_x > guard["x"]:
          guard["x"] += GUARD_SPEED
          guard["direction"] = "east"
      # ... and the same for west (x smaller), south (y bigger) and north (y smaller)
  ```
- `draw_guards()` draws a red square of `GUARD_HITBOX_SIZE` centred on each guard
  (`pygame.Rect` + `rect.center = (x, y)` + `pygame.draw.rect`, like `player_hitbox()`).
- In `update_and_draw_dungeon()` (in `screens.py`): call `move_guards()` just after
  `move_player(...)`, and `draw_guards()` after `draw_level(...)` but **before** `draw_player()`
  and `draw_fog(...)`. The fog hides the guards that are far away or behind a wall. That's on
  purpose: it's a dream, you only see them when they're close!

**Done when:** a red square walks back and forth in the top corridor, without stopping, and
stays hidden in the fog until you get close.

#### F2: A touch costs 20 seconds (≈ 30 min)
- New constants at the top of `guards.py`:
  - `GUARD_PENALTY = 20` (seconds of dream lost when a guard touches the Weaver)
  - `GUARD_PROTECTION = 2` (seconds after a touch when the guards can't touch again)
  - and a global `last_touch = None` (when a guard last touched the Weaver).
- **Why a protection?** A guard needs about half a second to walk through the Weaver: that's
  30 frames. Without it, the guard would take 20 s at *every* frame, so 600 s at once!
- `player_is_protected()` returns `True` while less than `GUARD_PROTECTION` seconds have passed
  since `last_touch` (and `False` if `last_touch` is `None`).
- `guard_touches_player()` returns `True` only at the start of a touch:
  - while `player_is_protected()`, return `False` straight away;
  - otherwise, check if the player's hitbox touches the hitbox of a guard. `import player`, then
    `player.player_hitbox(player.player_x, player.player_y)`. Not `from player import player_x`:
    that would be a copy that never moves (see `CLAUDE.md`). Two `pygame.Rect` touch when
    `rect_1.colliderect(rect_2)` is `True`;
  - when they touch, set `last_touch = time.time()` (with `global last_touch`) and return `True`.
- In `screens.py`, add a global `time_lost = 0` next to `dungeon_start`. In
  `update_and_draw_dungeon()`:
  - if `guard_touches_player()`, add `GUARD_PENALTY` to `time_lost`;
  - take it away from the time left:
    `time_left = Dream_time - (time.time() - dungeon_start) - time_lost`;
  - there's nothing else to do for the end: when `time_left` reaches 0, the timer already goes
    to WAKE_UP.
- Show that something happened, while `player_is_protected()`:
  - the player blinks: don't call `draw_player()` one tenth of a second out of two
    (`int(time.time() * 10) % 2 == 0`);
  - a red `"-20 s"` above the player, with `draw_label(...)`, **after** `draw_fog(...)`.
- In `reset_game()`: set `time_lost = 0` and call `reset_guards()` (which also sets `last_touch`
  back to `None`), so the next game starts fresh.

**Done when:** touching the guard takes exactly 20 s from the timer (not more), the player
blinks for 2 s, 3 touches show the wake up screen, and after SPACE the timer is full again.

#### F3: Three guards (≈ 15 min)
- Add guards 2 and 3 to `GUARD_ROUTES` (look at the table above):
  ```python
  GUARD_ROUTES = [
      ((6, 2), (14, 2)),         # top corridor: the easy one, pass on row 1
      ((11, 10.5), (18, 10.5)),  # big room before the door: blocks rows 10 and 11
      ((4, 15.5), (15, 15.5)),   # bottom corridor to the key: blocks rows 15 and 16
  ]
  ```
- `tile_center` works with 10.5 too: it gives the line between the two rows.

**Done when:** you can get the key and open the door without being touched, but you have to wait
for the right moment several times. **Testing tip:** to check a guard, walk straight into it and
look at the timer.

#### F4: The guard pictures (≈ 20 min)
- In `guards.py`, load the pictures from `grafiki/guard/` exactly like `player.py` does:
  `guard_images` (4 PNGs) and `guard_walking_images` (4 GIFs, with `load_animation`).
- In `draw_guards()`, replace the red square: the guards are always walking, so always show the
  walking animation of `guard["direction"]`, centred on the guard (copy the end of
  `draw_player()`). If a direction has no GIF, use its PNG.
- Bonus: a soft red glow under each guard, with `make_glow(...)` from `player.py` (like the cyan
  glow under the player, but with `color=(220, 70, 90)`). Make it once, at the top of the file.

**Done when:** the guards look like dream projections and face the way they walk.

#### F5: The sounds (≈ 15 min)
- Add `"guard_touch"` to `sounds` in `assets.py`, and play it when a guard touches the player
  (next to `time_lost += GUARD_PENALTY`). Thanks to the protection, it plays only once per touch.
- Bonus, `guard_near`: the fog hides the guards, so whispers warn you that one is close.
  - Add `GUARD_HEAR_DISTANCE = 200` (pixels) at the top of `guards.py`.
  - Each frame, if a guard is closer than that to the player, play `guard_near`, but only if it
    isn't already playing: the same trick as `locked_door_bump` in `door_try()` (`player.py`),
    with `get_num_channels() == 0`.
  - The distance between two points: `math.hypot(x1 - x2, y1 - y2)`.

**Done when:** a touch makes a sound (once, not every frame), and (bonus) you hear whispers
before you see a guard.

#### F6: Polish and balance (optional, pick what you like)
- **The right message:** if the guards took some time, the WAKE_UP screen could say it, for
  example `"The projections took 40 s of the dream!"` (use `time_lost` from `screens.py`, but
  show it before `reset_game()` puts it back to 0).
- **Balance:** play 3 times. Too hard? Try `GUARD_PENALTY = 10`, `GUARD_SPEED = 1`, or more time
  for the dream (`Dream_time`, because waiting for the guards takes time). Too easy?
  `GUARD_PENALTY = 30` or `GUARD_SPEED = 3`.
- **Still too hard?** Delete guard 1 from `GUARD_ROUTES`: 2 guards are enough for level 1.

**Done when:** the full game works twice in a row (touched once and still win, then lose because
of the guards), then commit: `feat: add the guards`.

### Improvement G: The weaving mini-game, step by step

The goal: opening the door doesn't weave the dream by itself any more. The Weaver has to weave it,
like in **Dance Dance Revolution**: coloured arrows climb up 4 lanes, and when an arrow reaches the
grey arrows at the top (the *loom*), you press the same arrow key. Each good key weaves one
coloured thread into the cloth on the right, and a missed key leaves a hole in it. Weave at least
60% of the threads and the dream holds (WEAVING screen, then the choice 1/2/3). Fewer, and the
threads break: SPACE to weave again.

```
 ... DUNGEON --door with the key--> LOOM --enough threads--> WEAVING --> choice 1/2/3 ...
                                     ^  |
                                     +--+ not enough threads: SPACE to weave again
```

Everything is in a new file, `loom.py`, and `draw_loom_screen()` in `screens.py` shows the rules,
the song and the result.

#### G0: What to create (ElevenLabs and Suno) (done)

The game works without them, but a dance game is much better with sounds.

**Sounds in ElevenLabs (Sound Effects).** Save them in `sound/` with these names. They must be
**very short**, or they will still be playing when the next arrow arrives:

| File | When | Length | Prompt |
|---|---|---|---|
| `loom_hit.mp3` | a good key: a thread is woven | ~0.3 s | `A single soft magical pluck of a harp string with a quick wooden loom shuttle click, bright and dreamy, very short, no reverb tail, no music.` |
| `loom_miss.mp3` | a missed arrow | ~0.4 s | `A thin thread snapping with a soft dull pop, short and gentle, a little sad but not scary, no music.` |

**Music in Suno (bonus, G5).** The song of the loom, so you dance on a real beat:
```
Instrumental, 100 BPM, steady four-on-the-floor beat with a clear kick on every beat,
dreamy synthwave with harp arpeggios and a soft cinematic pad, mysterious heist mood,
no vocals, 35 seconds.
```
Save it as `music/loom_song.mp3`. The **100 BPM** is important: it must be the same as `LOOM_BPM`
in `loom.py`, or the arrows won't follow the music.

#### G1: The song and the arrows (done)
- In `loom.py`, `SONG` is a text with one letter per half beat: `L` left, `D` down, `U` up,
  `R` right, `.` nothing. `reset_loom()` turns each letter into a dictionary: its lane, the time it
  must be pressed (in seconds after the start of the song) and its result (`None` = not played yet).
- `draw_loom()` draws each arrow at `TARGET_Y + (note time - song time) * SCROLL_SPEED`: when its time
  comes, it is exactly on the loom. A time in the future means lower on the screen.

**Done when:** arrows climb up the 4 lanes and pass over the grey arrows of the loom.

#### G2: Press at the right moment (done)
- `judge_keys(game.keys_down)` checks the keys pressed *this frame* (like SPACE, so holding a key
  only counts once). For the right lane, the first arrow less than `GOOD_WINDOW` seconds away from
  the loom is woven: `"PERFECT"` if it is closer than `PERFECT_WINDOW`, `"GOOD"` otherwise.
- An arrow more than `GOOD_WINDOW` seconds late is `"MISS"`.
- `draw_loom_screen()` shows the last result under the loom for `JUDGEMENT_DURATION` seconds,
  and the grey arrow lights up in colour.

**Done when:** pressing on time says PERFECT, a bit late says GOOD, not at all says MISS.

#### G3: The cloth and the result (done)
- `draw_cloth()`: the vertical threads (the *warp*) are always there. One horizontal thread per
  woven arrow, from the bottom up, in the colour of its lane. Over, under, over, under: like on the
  WEAVING screen, one warp thread out of two goes back on top.
- When the song is over (`loom_finished()`): with at least `threads_needed()` threads, SPACE goes to
  WEAVING. Otherwise SPACE plays the song again.
- `reset_game()` calls `reset_loom()`, so the next game starts with an empty cloth.

**Done when:** you can win the mini-game, lose it and try again, then play a full game twice.

#### G4: The sounds (done)
- `"loom_hit"` and `"loom_miss"` are in `sounds` in `assets.py`.
- In `judge_keys()`, `sounds["loom_hit"]` plays next to `lane_flash[lane] = now`, and
  `sounds["loom_miss"]` next to `note["result"] = "MISS"`.

**Done when:** each good key plucks a string and each miss snaps a thread.

#### G5: Dance on the music (done)
- `start_music()` in `assets.py` can now play any file of the `music` folder:
  `start_loom()` plays `loom_song.mp3` once (`loops=0`), at the same time as the arrows start.
  SPACE on the "dream is woven" message puts the normal music back with `start_music()`.
- The beat must fall on the arrows. Measured with ffmpeg: the music is exactly 100 BPM and its
  first beat is at 0.13 s, so `MUSIC_START = 0.13` is added to the time of every note.
- The music has parts: soft (beats 0 to 8), drums (8 to 24), loud (24 to 54), then it ends.
  `SONG` has one line per 8 beats, so the dance gets harder when the music gets loud.
- **If the arrows feel a little early or late** on your computer, change `MUSIC_START` by small
  steps (0.05): bigger if the music comes after the arrows, smaller if it comes before.

**Done when:** the arrows reach the loom exactly on the beats of the music.

#### G6: Polish (optional, pick what you like)
- **Harder:** a faster `SCROLL_SPEED`, a smaller `GOOD_WINDOW`, more letters and fewer dots in
  `SONG`, or `PASS_PERCENT = 80`. Don't change `LOOM_BPM`: it must stay the tempo of the music.
- **Combo:** count the good keys in a row and show `Combo x12` under the result.
- **No cheating:** right now, pressing all the keys all the time works quite well! A key pressed
  with no arrow near the loom could also count as a `"MISS"`.
- **Score on the WIN screen:** "You wove 37 threads out of 40!"

**Done when:** the full game works twice in a row, then commit: `feat: add the weaving mini-game`.

### Improvement H: Level 2, a deeper dream, step by step

The goal: like in *Inception*, there is a dream **inside** the dream. When the Weaver opens the
door of level 1, there's no weaving yet: Mr. Banks falls into a deeper dream, with a new maze, a
new key, a new door and new guards. The weaving (and the choice 1/2/3) only comes after the door
of **level 2**.

```
 ... DUNGEON (level 1) --door--> DEEPER --SPACE--> TRANSITION --> DUNGEON (level 2) --door--> WEAVING ...
```

The big idea: the code already plays **one map**. You won't write a second dungeon: you'll teach
the game to **swap the map** (and the guards) for another one, then play it the same way.

This time the steps say *what* to do and give hints, but not the full code: you've already done
all the tricks in improvements C and F. When you're stuck, look for the same idea in the code
that already works. Same as before: don't move on before **"Done when…"** passes, and commit
after each step.

#### H0: Imagine level 2 (≈ 30 min, on paper)
- **The story:** where is the Weaver now? An idea: level 1 is Mr. Banks's house, level 2 is
  **the bank vault in his dream**, where the idea of the transfer must be planted.
- **The map:** draw it on squared paper, 20 columns × 18 rows, with the same letters as level 1
  (`W` `.` `P` `K` `D`). The rules:
  - The **whole border is `W`**. That's not only for the look: the fog and the walls read the
    tile next to the player, and outside the map there is no tile, so the game would crash.
  - Exactly **one** `P`, one `K` and one `D`.
  - Every row has **exactly 20 letters**, and there are **exactly 18 rows**.
  - Make sure you can walk from `P` to `K`, then from `K` to `D` (follow it with a pencil!).
  - Level 2 should be a bit harder than level 1: longer, with more dead ends.
- **The guards:** on the same paper, draw their routes like in the table of improvement F (one
  number per guard). A route is a **straight line** (one row, or one column: guards can now walk
  up and down too!), only on floor tiles, and there must always be a safe place to wait next to it.

**Done when:** the map and the guard routes are on paper, and someone else (not the one who drew
it) managed to follow the path from `P` to `K` to `D` with a finger.

#### H1: One map that can change (≈ 30 min)
Today `LEVEL_1` is both *the map of level 1* and *the map being played* (picking up the key
rewrites a row of it). With 2 levels, that has to be 2 different things:
- `LEVEL_1` (and soon `LEVEL_2`) = the map **as it is at the start**. It never changes.
- `dungeon_map` = the map **being played now**. This one changes: the key disappears from it,
  and it becomes level 2 when you go deeper.

In `level.py`:
- Keep `LEVEL_1`, but remove `LEVEL_1_START` (it was a copy of the start map: `LEVEL_1` is now
  that start map).
- Add `LEVELS = [LEVEL_1]` (the list of all the levels, in order), `level_number = 0` (0 = the
  first level, because lists start at 0) and `dungeon_map = list(LEVEL_1)`.
- Replace `reset_level()` by `load_level(number)`: it remembers `number` in `level_number` (don't
  forget the `global` line) and copies `LEVELS[number]` into `dungeon_map`. Look at how
  `reset_level()` does it: with `[:]`, to change the list itself and not make a new one.

Then use `dungeon_map` everywhere `LEVEL_1` was used to *play*: in `player.py`, `fog.py` and
`screens.py`. **Tip:** in VS Code, `Cmd + Shift + F` and search `LEVEL_1` to find them all.
In `screens.py`, `reset_game()` now calls `load_level(0)` instead of `reset_level()`.

**Why does `from level import dungeon_map` still work?** Read the *Shared state* part of
`CLAUDE.md`: it's a list that is changed *in place*, so every file sees the same one.

**Done when:** the game plays **exactly like before** (key, door, guards, play again twice).
Nothing new on screen: that's normal, and it's the hardest step! Commit:
`refactor: separate the start map from the map being played`.

#### H2: Type in the map of level 2 (≈ 30 min)
- In `level.py`, type your paper map as `LEVEL_2`, under `LEVEL_1`, and add it to `LEVELS`.
- **Check the size:** a missing letter is very hard to see. Put this at the bottom of
  `level.py` for a moment, it prints the rows that are wrong:
  ```python
  for row_number, row in enumerate(LEVEL_2):
      if len(row) != 20:
          print("row", row_number, "has", len(row), "letters")
  print(len(LEVEL_2), "rows")
  ```
- **To see it in the game** without playing level 1 first: for a moment, write
  `dungeon_map = list(LEVEL_2)` instead of `list(LEVEL_1)`. The guards of level 1 will walk at
  strange places (maybe through walls): don't worry, H4 fixes that.

**Done when:** the game starts on level 2, the player is on `P`, you can take the key and open the
door. Then put back `list(LEVEL_1)`, remove the `print` lines, and commit.

#### H3: The DEEPER screen (≈ 45 min)
A new screen, between the two levels. You did it for WAKE_UP: follow the 4 steps from
`CLAUDE.md` (section *Architecture*).
1. Add `"DEEPER"` to `STATES` in `game.py`.
2. In `screens.py`, write `draw_deeper_screen()`: a background colour (or a picture), and a
   `draw_message([...])`, for example:
   ```
   The door opens on a staircase...
   Mr. Banks falls into a deeper dream.
   Press SPACE to follow him.
   ```
   When SPACE is pressed, start level 2, then `game.state = "TRANSITION"`.
3. In `main.py`, import it and add its `elif`.
4. (Optional) A sound when it starts, in `SCREEN_SOUNDS`.

**Starting a level** needs a lot of resets: the map, the player on the new `P` without the key,
the guards, and a full timer (`dungeon_start` and `time_lost`). `reset_game()` already does
almost all of it! Write a new function `start_level(number)` in `screens.py` with that part,
and make `reset_game()` call `start_level(0)`.
- **The order matters:** `reset_player()` looks for the `P` in `dungeon_map`. Which one must
  come first, `load_level(...)` or `reset_player()`?

**The door now has 2 jobs.** In `door_try()` (`player.py`), with the key:
- if this is **not** the last level, go to `"DEEPER"`;
- if it **is** the last level, go to `"WEAVING"` like before.
- How do you know it's the last level? `level_number` is `0` or `1`, and `len(LEVELS)` is `2`.
- `level_number` changes during the game, so `import level` and write `level.level_number`,
  never `from level import level_number`: that would be a copy that stays at 0 forever.

**Done when:** level 1's door shows the DEEPER screen, SPACE plays the transition, then level 2
starts with the player on its `P`, a key, and a full timer. Level 2's door goes to WEAVING. After
the WIN screen, SPACE goes back to **level 1**.

#### H4: The guards of level 2 (≈ 30 min)
Right now every level has the guards of level 1. Each level needs its own list of routes.
- In `guards.py`, turn `GUARD_ROUTES` into a **list of lists**: one list of routes per level,
  in the same order as `LEVELS`:
  ```python
  GUARD_ROUTES = [
      [ ... the 3 routes of level 1, as today ... ],
      [ ... the routes of level 2, from your paper ... ],
  ]
  ```
- In `reset_guards()`, only take the routes of the level being played:
  `GUARD_ROUTES[level.level_number]` (the same `import level` trick as in H3).
- **Vertical routes work already:** `move_guards()` handles north and south, and the guard
  pictures exist for the 4 directions. Only one small thing: a new guard starts facing `"east"`.
  For a vertical route that's wrong during the first steps. Can you fix it? (Hint: compare the
  rows of `start` and `end`.)
- To check a route: walk straight into the guard, it should take 20 s.

**Done when:** level 1 has its 3 guards like before, level 2 has its own guards on their paper
routes, and after losing on level 2 (WAKE_UP), the next game has the guards of level 1 again.

#### H5: Make it feel deeper (optional, pick what you like)
- **Show the level:** `"Level 2"` somewhere on the screen of the dungeon, with `draw_label(...)`
  (after the fog, or the fog hides it!).
- **The right transition text:** `"Entering the dream of Mr. Banks..."` for level 1, and
  `"Going deeper into the dream..."` for level 2 (use `level.level_number`).
- **More time for a bigger maze:** `Dream_time` can become a list, `[60, 90]`, one per level.
- **Harder guards:** a speed per level (`GUARD_SPEEDS = [2, 3]`), or more guards.
- **Try again from level 2:** losing on level 2 sends you back to level 1. Kinder: the WAKE_UP
  screen could call `start_level(level.level_number)` and go to TRANSITION, so you try level 2
  again (but then, how do you go back to the MISSION screen?).
- **New pictures for level 2:** a vault floor and vault walls made in PixelLab (40 × 40, the same
  settings as the level 1 tiles), for example *"top-down pixel art tile, floor of a golden bank
  vault, dreamy purple light"*. Save them as `grafiki/tiles/floor_2.png` and `wall_2.png`, then
  `draw_level()` picks the pictures of the level being played.
- **Docs:** update the screen flow in `CLAUDE.md` (TITLE → MISSION → ...) with the DEEPER screen.

**Done when:** you can play the full game twice in a row: level 1, DEEPER, level 2, weaving, win,
and once losing on level 2. Then commit: `feat: add level 2, a deeper dream`.

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
