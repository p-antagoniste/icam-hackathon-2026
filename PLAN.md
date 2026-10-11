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
| H | **Mission 2, a new target** | ★★☆ | After the WIN screen, a new mission with a new target, a harder maze and a harder dance on the loom. Easy once levels are lists of strings: `LEVELS = [LEVEL_1, LEVEL_2]` (step by step below) |
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
- Before the song, the rules stay on the screen for `RULES_DURATION` seconds with a countdown,
  then the song starts by itself (SPACE starts it sooner).
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

### Improvement H: Mission 2, a new target, step by step

**The goal:** after the WIN screen, the game isn't over. The anonymous client sends a **second
mission**, with a **new target**, a new maze (a bit harder), new guards and a new dance on the
loom (a bit harder too). After the second WIN screen, the game is over and goes back to the title.

```
 MISSION 1 --> TRANSITION --> DUNGEON (maze 1) --> LOOM (dance 1) --> WEAVING --> WIN 1
                                                                                   |
     +-------------------------------- SPACE: next mission <-----------------------+
     v
 MISSION 2 --> TRANSITION --> DUNGEON (maze 2) --> LOOM (dance 2) --> WEAVING --> WIN 2 --SPACE--> TITLE
```

If the President wakes up (WAKE_UP screen), SPACE tries **mission 2 again**, not mission 1.

What is different in mission 2:

| | Mission 1 | Mission 2 |
|---|---|---|
| Target | Mr. Banks, senior banker | **Emmanuel Macron**, President of France |
| What to weave | "transfer 1,000,000 € to account FR76 ... 0042" | "give all your powers to the anonymous client" |
| The dream | Mr. Banks's house | The Élysée Palace: golden rooms and long corridors |
| Maze | `LEVEL_1` | `LEVEL_2`: longer, more dead ends |
| Guards | 3, walking left and right | 4, one walking up and down |
| Loom | 47 arrows, need 60% | 69 arrows, a bit faster, need 65% |
| Ending | the choice 1/2/3 | one ending, then THE END |

#### Before you start: the trick of this whole improvement

The game needs to know which mission is being played. That's **one number**:
`game.mission_number`. It is `0` during mission 1 and `1` during mission 2 (in Python, lists
start at 0, so the first mission is number 0).

Everything that is different in mission 2 becomes a **list with 2 values**: the value for
mission 1, then the value for mission 2. And the code takes the right one with
`[game.mission_number]`:

```python
TARGET_NAMES = ["Mr. Banks", "Emmanuel Macron"]

TARGET_NAMES[0]                    # "Mr. Banks"
TARGET_NAMES[1]                    # "Emmanuel Macron"
TARGET_NAMES[game.mission_number]  # the name of the target of the mission being played
```

That's it! Each step below uses this trick on a different part of the game.

**How the steps work.** Each step says which file to open, what to find in it, and what to write
instead. Do the steps in order, test after each one, and commit when the test works. Three useful
keys in VS Code:
- `Cmd + F`: find a word in the open file;
- `Cmd + Option + F`: find a word **and replace it** in the open file ("Replace All" changes them
  all at once);
- `Cmd + Shift + F`: find a word in **all the files** of the game.

#### H0: Imagine mission 2 (≈ 30 min, on paper)

**Goal:** the story, the map of level 2 and where its guards walk, all on paper.

1. **The story.** The target is Emmanuel Macron, the President of France. With the money of
   mission 1, the anonymous client wants more: **all the powers of the President**. Think about
   what the client says in the mission message, and what happens the next morning (the ending).
2. **The map.** On squared paper, draw a rectangle of **20 squares wide and 18 squares high**.
   Each square is one tile: `W` wall, `.` floor, `P` start, `K` key, `D` door. Check these rules:
   - [ ] the **whole border is `W`** (otherwise the game crashes when you walk to the edge);
   - [ ] there is exactly **one** `P`, **one** `K` and **one** `D`;
   - [ ] you can walk from `P` to `K`, then from `K` to `D` (follow it with a pencil!).
3. **A bit harder, not much harder.** Pick 2 or 3 of these ideas:
   - put `P`, `K` and `D` in 3 different corners, so the path is longer;
   - add dead ends (in the fog, you only see them once you're inside);
   - add a few corridors only 1 tile wide (scary in the fog);
   - hide the key at the end of a dead end, behind a turn.
4. **The guards.** Draw 4 guard routes on the map, like in the table of improvement F (write the
   number of the guard on each tile it walks on). A route is a **straight line**: on one row
   (left and right) or on one column (up and down). Check:
   - [ ] the route is only on floor tiles, never through a wall;
   - [ ] **no guard in a corridor 1 tile wide**: you couldn't let it go by, it would always touch you;
   - [ ] next to each route there is a safe place to wait (a side passage, a corner, a room).

**Done when:** everything is on paper, and someone else (not the one who drew it) can follow the
path from `P` to `K` to `D` with a finger.

#### H1: Make the pictures (Gemini, and PixelLab as a bonus) (done)

**Goal:** the pictures of mission 2, ready for step H5. You can do this step while someone else
does H2 to H4.

To get the same style as mission 1, **give Gemini the old picture** together with the prompt.

**1. The portrait of the target.** Give Gemini `grafiki/mr_banks.jpeg`, ask for a square picture,
and save it as `grafiki/president.jpeg`. Gemini refuses to draw some real people, like the
President, so the picture is an **invented President of France**. That's fine: in a game, a
picture can play the role of a real person, like an actor in a film.
```
In exactly the same pixel art style as this picture: a polaroid photo held by a paperclip,
slightly tilted, on a very dark navy blue background. In the photo: an invented President of
France, a man in his sixties with grey hair and a neat grey beard, in a dark blue suit and a
blue tie, in a golden palace office, with a French flag and a European flag behind him. A red
marker circle is drawn around his face. A friendly cartoon character, not a real person.
```

**2. The ending.** Give Gemini `grafiki/win_screen.jpeg`, ask for a landscape picture, and save it
as `grafiki/win_screen_2.jpeg`:
```
In exactly the same pixel art style as this picture: the next morning, the President of France
(the man of the second picture) sits at his golden desk in a palace and signs an official paper
with a big red seal. Glowing dream threads (gold, cyan and red) float around his head. On
a big screen behind him, the cyan silhouette of a man with a hat and glowing eyes smiles. The
bottom quarter of the picture is dark and simple, with nothing important in it.
```
Also give Gemini `president.jpeg`, so it's the same man. The bottom must stay empty because the
message panel goes there.

**3. Bonus: the tiles of the palace** in PixelLab (40 × 40, top-down, the same settings
as the tiles of level 1). They're used in H8:
- `grafiki/tiles/floor_2.png`:
  `top-down pixel art floor tile, French palace, golden wooden parquet floor with a diamond pattern, dreamy purple light`
- `grafiki/tiles/wall_2.png`:
  `top-down pixel art wall tile, a white palace wall with golden ornaments, seen from above, dreamy purple light`

No new sound or music is needed: the dance of mission 2 uses the same music.

**Done when:** `president.jpeg` and `win_screen_2.jpeg` are in `grafiki/`.

#### H2: One map that can change (≈ 30 min)

**Goal:** prepare the game to play more than one map. Nothing changes on the screen yet.

**Why?** Today `LEVEL_1` has 2 jobs: it is the map of level 1, **and** the map being played (when
you pick up the key, the `K` becomes a `.` in `LEVEL_1`). With 2 levels, we need 2 different
things:
- `LEVELS`: the maps **as they are at the start**, one per mission. They never change.
- `dungeon_map`: the map **being played now**. The key disappears from it, and during mission 2
  it becomes a copy of level 2.

**Files:** `level.py`, `player.py`, `fog.py`, `screens.py`.

1. In `level.py`, find:
   ```python
   # A copy of the map as it is at the start: picking up the key changes LEVEL_1
   LEVEL_1_START = list(LEVEL_1)
   ```
   and replace it with:
   ```python
   # All the maps, one per mission, as they are at the start. They never change
   LEVELS = [LEVEL_1]

   # The map being played now. Picking up the key changes it (the K becomes a .)
   dungeon_map = list(LEVEL_1)
   ```
2. Still in `level.py`, find the function `reset_level()`:
   ```python
   def reset_level():
       # Put the key back for a new game.
       # [:] changes the list itself, so the files that imported LEVEL_1 see the new map too
       LEVEL_1[:] = LEVEL_1_START
   ```
   and replace it with:
   ```python
   def load_level(number):
       # Copy the start map of a level into the map being played (so the key is back).
       # [:] changes the list itself, so the files that imported dungeon_map see the new map too
       dungeon_map[:] = LEVELS[number]
   ```
3. In `player.py`, press `Cmd + Option + F`, find `LEVEL_1`, replace with `dungeon_map`, and click
   **Replace All**. The first line it changes is the `import` at the top: it now reads
   `from level import dungeon_map, TILE_SIZE, find_tile`.
4. In `fog.py`: the same, replace all `LEVEL_1` with `dungeon_map`.
5. In `screens.py`, change 3 lines:
   - at the top, `from level import LEVEL_1, draw_level, reset_level` becomes
     `from level import dungeon_map, LEVELS, draw_level, load_level`;
   - in `update_and_draw_dungeon()`, `draw_level(LEVEL_1)` becomes `draw_level(dungeon_map)`;
   - in `reset_game()`, `reset_level()   # the key is back in the maze` becomes
     `load_level(0)   # the map of level 1, with its key`.
6. Press `Cmd + Shift + F` and search `LEVEL_1`: in the `.py` files, it must now only be in
   `level.py` (it's also in `PLAN.md` and `CLAUDE.md`, that's fine).

**Why does `from level import dungeon_map` work?** Usually, `from ... import` makes a copy that
never sees the changes. But `dungeon_map` is a list that is only changed *in place* (with `[:]`,
or by changing one row): it stays the same list, so every file sees the changes. See the *Shared
state* part of `CLAUDE.md`.

**Done when:** the game plays **exactly like before**: the key disappears when you take it, the
door opens, and when you play again the key is back. Nothing new on the screen is normal!
**Commit:** `refactor: separate the start map from the map being played`.

#### H3: Type in the map of level 2 (≈ 30 min)

**Goal:** the paper map of H0 becomes `LEVEL_2` in the code.

**File:** `level.py`.

1. Under `LEVEL_1` (after its `]`), copy this empty room. It has the right size and the border is
   already there: change the dots into your walls, and add your `P`, `K` and `D`. Don't add or
   remove letters, only change them!
   ```python
   # Mission 2: the Elysee Palace, in the dream of the President
   LEVEL_2 = [
       "WWWWWWWWWWWWWWWWWWWW",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "W..................W",
       "WWWWWWWWWWWWWWWWWWWW",
   ]
   ```
   **Tip:** each row must keep 20 letters. When you type a `W`, delete a dot next to it.
2. Add it to the list of levels: `LEVELS = [LEVEL_1]` becomes `LEVELS = [LEVEL_1, LEVEL_2]`.
3. **Check the size.** A missing letter is very hard to see. Put this at the very bottom of
   `level.py` for a moment and run the game: the terminal shows the rows that are wrong.
   ```python
   for row_number, row in enumerate(LEVEL_2):
       if len(row) != 20:
           print("row", row_number, "has", len(row), "letters")
   print(len(LEVEL_2), "rows")
   ```
   You want no "row ... has ..." line, and `18 rows`.
4. **Try it** without playing mission 1 first: for a moment, change
   `dungeon_map = list(LEVEL_1)` into `dungeon_map = list(LEVEL_2)`. The guards of level 1 will
   walk at strange places (maybe through walls): that's normal, H6 fixes it.

**Done when:** the game starts in level 2, the player is on `P`, and you can take the key and open
the door. Then **undo step 4** (back to `list(LEVEL_1)`) and remove the lines of step 3.
**Commit:** `feat: add the map of level 2`.

#### H4: The mission number (≈ 45 min)

**Goal:** after the first WIN screen, SPACE starts mission 2 in the maze of level 2. After the
second WIN screen, the game goes back to the title.

**Files:** `game.py`, `screens.py`.

1. In `game.py`, under the line `state = "TITLE"`, add:
   ```python
   # The mission being played: 0 = mission 1, 1 = mission 2 (lists start at 0).
   # Like game.state, always write game.mission_number: "from game import mission_number"
   # would make a copy that stays at 0 forever
   mission_number = 0
   ```
2. In `screens.py`, in `reset_game()`, change `load_level(0)` into
   `load_level(game.mission_number)`. Now `reset_game()` prepares the mission being played.
   Keep this line **above** `reset_player()`: `reset_player()` looks for the `P` in the map, so
   the map of the right level must be loaded first.
3. Still in `screens.py`, in `draw_win_screen()`, the 3 endings all finish with the same 3 lines.
   **Delete them, all 3 times:**
   ```python
           if pygame.K_SPACE in game.keys_down:
               reset_game()
               game.state = "MISSION"
   ```
   Then write this **once**, at the very end of the function. It starts with 4 spaces, like the
   `if THE_VICTORY_NUMBER == 1:` line:
   ```python
       # SPACE: the next mission, or the end of the game after the last mission
       if pygame.K_SPACE in game.keys_down:
           if game.mission_number < len(LEVELS) - 1:
               game.mission_number = game.mission_number + 1
               reset_game()
               game.state = "MISSION"
           else:
               game.mission_number = 0
               reset_game()
               game.state = "TITLE"
   ```
   **Why `len(LEVELS) - 1`?** There are 2 levels, so `len(LEVELS)` is 2, and the last mission is
   number `1` (because the first one is `0`). "Smaller than 1" means "not the last mission yet".
   And `reset_game()` comes **after** the change of `game.mission_number`: it must prepare the
   new mission, not the old one.
4. In the 3 messages of `draw_win_screen()`, change `"Press SPACE to play again."` into
   `"Press SPACE for the next mission."`.

You don't need to change anything else:
- WAKE_UP already calls `reset_game()`: it now prepares **the same mission** again;
- the door, with the key, still goes to the loom.

**Done when:**
- [ ] after WIN 1, SPACE shows the MISSION screen (still about Mr. Banks: that's H5), then the
      maze of level 2;
- [ ] after WIN 2, SPACE goes back to the title, and a new game starts in level 1;
- [ ] waking up in level 2 tries level 2 again.

**Commit:** `feat: go to mission 2 after the first win`.

#### H5: The screens of mission 2 (≈ 45 min)

**Goal:** the screens tell the story of the mission being played: the right target, the right
name, the right ending.

**File:** `screens.py`. The pictures of H1 are ready in `grafiki/`:
- `president.jpeg`: the polaroid of the President, for the MISSION screen (square, like
  `mr_banks.jpeg`);
- `win_screen_2.jpeg`: the next morning, the President signs the paper, for the WIN screen of
  mission 2. Like `win_screen.jpeg`, its bottom is dark, so the message panel goes there.

1. **The lists.** At the top, in the `MISSION` section, under the line
   `banks_image = load_picture(...)`, add:
   ```python
   # Made with Gemini too, from mr_banks.jpeg so it has the same style
   president_image = load_picture((PORTRAIT_SIZE, PORTRAIT_SIZE), "president.jpeg")

   # One value per mission: [mission 1, mission 2]
   TARGET_NAMES = ["Mr. Banks", "Emmanuel Macron"]
   target_images = [banks_image, president_image]
   MISSION_TEXTS = [
       [   # mission 1
           "INCOMING MESSAGE",
           " Target:   Mr. Banks, senior banker.",
           " Mission:  Enter his dream tonight.",
           "           Make him believe he must transfer",
           "           1,000,000 € to account FR76 ... 0042.",
           " Payment:  generous.",
           " Press SPACE to accept the mission.",
       ],
       [   # mission 2
           "INCOMING MESSAGE",
           " Target:   Emmanuel Macron, President of France.",
           " Mission:  Enter his dream tonight.",
           "           Make him believe he must give",
           "           all his powers to me.",
           " Payment:  much more than last time.",
           " Press SPACE to accept the mission.",
       ],
   ]
   ```
   And in the `WIN` section, under the line `win_image3 = load_background(...)`:
   ```python
   # Made with Gemini: the next morning, the President signs. Its bottom is dark too
   win_image_mission_2 = load_background("win_screen_2.jpeg")
   ```
   **Check the names:** a picture name must be written exactly like the file in `grafiki/`
   (`president.jpeg`, not `president.jpg`), or the game stops at once with an error.
2. **MISSION screen.** In `draw_mission_screen()`, 3 changes:
   - the line `screen_surface.blit(banks_image, banks_image.get_rect(midtop=(target_x, PORTRAIT_TOP)))`
     becomes 2 lines:
     ```python
     target_image = target_images[game.mission_number]
     screen_surface.blit(target_image, target_image.get_rect(midtop=(target_x, PORTRAIT_TOP)))
     ```
   - `"The target: Mr. Banks"` becomes `"The target: " + TARGET_NAMES[game.mission_number]`;
   - the long line `textes = ["INCOMING MESSAGE", ...]` becomes
     `textes = MISSION_TEXTS[game.mission_number]`.
3. **TRANSITION screen.** In `draw_transition_screen()`, `"Entering the dream of Mr. Banks..."`
   becomes `"Entering the dream of " + TARGET_NAMES[game.mission_number] + "..."`.
4. **WAKE_UP screen.** In `draw_wake_up_screen()`, `"Mr. Banks woke up!"` becomes
   `TARGET_NAMES[game.mission_number] + " woke up!"`.
5. **WEAVING screen.** The choice 1/2/3 is about the transfer: it's only for mission 1. In
   `draw_weaving_screen()`, just **before** the line `textes = ["Chose the weath-in threds ", ...]`,
   add:
   ```python
       # Mission 2 has no choice: SPACE goes straight to the ending
       if game.mission_number == 1:
           draw_message(["The dream is woven.", "Press SPACE."])
           if pygame.K_SPACE in game.keys_down:
               game.state = "WIN"
           return
   ```
6. **WIN screen.** At the start of `draw_win_screen()`, the line `if THE_VICTORY_NUMBER == 1:`
   becomes `elif THE_VICTORY_NUMBER == 1:`, and just above it add the ending of mission 2:
   ```python
       if game.mission_number == 1:
           screen_surface.blit(win_image_mission_2, (0, 0))
           draw_message([
               "Mission complete.",
               "The President gave all his powers to... ???",
               "Press SPACE to finish the game.",
           ], center_y=WIN_MESSAGE_Y)
   ```
   The 3 endings of mission 1 stay as they are, under it.

**Done when:**
- [ ] mission 2 shows the President's polaroid (not Mr. Banks), his mission text, his name in the
      transition, no choice after the weaving, and the picture of him signing as the ending;
- [ ] mission 1 looks exactly like before.

**Commit:** `feat: the story of mission 2`.

#### H6: The guards of mission 2 (≈ 30 min)

**Goal:** level 2 has its own guards, on the routes you drew in H0.

**File:** `guards.py`.

1. At the top, under `import player`, add `import game`.
2. `GUARD_ROUTES` becomes a **list of 2 lists**: the routes of mission 1, then the routes of
   mission 2. Replace it with this, and write your routes from the paper in the second list:
   ```python
   GUARD_ROUTES = [
       [   # mission 1
           ((6, 2), (14, 2)),         # top corridor: the easy one, pass on row 1
           ((11, 10.5), (18, 10.5)),  # big room before the door: blocks rows 10 and 11
           ((4, 15.5), (15, 15.5)),   # bottom corridor to the key: blocks rows 15 and 16
       ],
       [   # mission 2: (column, row) of the start -> (column, row) of the end
           ((1, 1), (5, 1)),          # an example: change it with your routes!
       ],
   ]
   ```
   **To find the column and the row of a tile,** count from 0, starting at the top left corner.
   This ruler helps: put it above your map, like in the table of improvement F.
   ```
              0         1
              01234567890123456789
      row  0  WWWWWWWWWWWWWWWWWWWW
      row  1  W..................W
   ```
   For a guard walking up and down, the column stays the same: `((8, 3), (8, 12))`.
3. In `reset_guards()`, take only the routes of the mission being played:
   `for start, end in GUARD_ROUTES:` becomes
   `for start, end in GUARD_ROUTES[game.mission_number]:`.
4. **Look the right way.** A new guard always starts looking `"east"`, so a guard walking down
   looks the wrong way at the start. In `reset_guards()`, just above `guards.append(...)`, add:
   ```python
           # At the start, the guard looks towards the end of its route
           if end[0] > start[0]:
               direction = "east"
           elif end[0] < start[0]:
               direction = "west"
           elif end[1] > start[1]:
               direction = "south"
           else:
               direction = "north"
   ```
   and in `guards.append(...)`, `"direction": "east"` becomes `"direction": direction`.

**Done when:**
- [ ] level 1 has its 3 guards like before;
- [ ] level 2 has its 4 guards, on the routes of the paper, and none walks through a wall;
- [ ] walking into a guard of level 2 takes 15 s.

**Commit:** `feat: the guards of mission 2`.

#### H7: A harder loom (≈ 30 min)

**Goal:** the dance of mission 2 has more arrows, a bit faster, and needs more threads.

**File:** `loom.py`.

1. At the top, under `import pygame`, add `import game`.
2. At the top of the file, **delete** these 3 lines (the lists of step 4 will replace them):
   ```python
   SCROLL_SPEED = 300        # pixels per second: how fast the arrows climb
   GOOD_WINDOW = 0.16        # ... and as "GOOD". Later than that, the thread is missed
   PASS_PERCENT = 60         # how many threads (in %) must be woven for the dream to hold
   ```
3. Now, everywhere the code used one of these 3 names, it must take the value of the mission
   being played. With `Cmd + Option + F` and **Replace All**:

   | Find | Replace with | How many |
   |---|---|---|
   | `GOOD_WINDOW` | `GOOD_WINDOWS[game.mission_number]` | 3 (in `judge_keys()` and `loom_finished()`) |
   | `* PASS_PERCENT` | `* PASS_PERCENTS[game.mission_number]` | 1 (in `threads_needed()`) |
   | `* SCROLL_SPEED` | `* SCROLL_SPEEDS[game.mission_number]` | 1 (in `draw_loom()`) |
   | `enumerate(SONG)` | `enumerate(SONGS[game.mission_number])` | 1 (in `reset_loom()`) |

   VS Code shows "1 of 3" (or "of 1") in the search box: check it's the same number as in the
   table before clicking Replace All. Do this step **before** step 4: after it, `GOOD_WINDOWS` is
   in the file too, and Replace All would change it as well!
4. Rename the song: `SONG = (` becomes `SONG_1 = (`. Then, under the `)` that closes `SONG_1`, add
   the song of mission 2 and the lists. It uses the same music and the same beats, but more arrows
   fall **between** the beats, and there are fewer dots:
   ```python
   SONG_2 = (
       "....L...R...L.R."  # beats 0-8: the soft start of the music
       "L.D.U.R.L.D.U.R."  # beats 8-16: the drums start
       "L.R.LDUR.R.L.URD"  # beats 16-24
       "L.DUR.UDL.RUD.LR"  # beats 24-32: the music gets loud
       "LDUR.RUDL.LDUR.."  # beats 32-40
       "LR.LR.UD.UD.LDUR"  # beats 40-48
       "LDURLDURL...L..."  # beats 48-56: the end of the music
   )

   # One value per mission: [mission 1, mission 2]
   SONGS = [SONG_1, SONG_2]
   SCROLL_SPEEDS = [300, 360]   # pixels per second: how fast the arrows climb
   GOOD_WINDOWS = [0.16, 0.14]  # seconds too early or too late that still count as "GOOD"
   PASS_PERCENTS = [60, 65]     # how many threads (in %) must be woven for the dream to hold
   ```
   You can change `SONG_2`, but each line must keep **exactly 16 letters**, or the arrows stop
   following the music.

**Forgot one?** Python tells you: the game stops with `NameError: name 'GOOD_WINDOW' is not
defined`, and the message gives the number of the line to fix.

`reset_game()` already calls `loom.reset_loom()`, so the arrows of the right song are ready at the
start of each mission.

**Done when:**
- [ ] in mission 1, the rules panel of the loom says "Weave 29 threads to win.", like before;
- [ ] in mission 2, it says "Weave 45 threads to win.", and the arrows are faster.

**Commit:** `feat: a harder loom for mission 2`.

#### H8: Polish (optional, pick what you like)
- **More time for a bigger maze.** In `screens.py`, `Dream_time = 60` becomes
  `DREAM_TIMES = [60, 75]`, and in `update_and_draw_dungeon()`, `Dream_time` becomes
  `DREAM_TIMES[game.mission_number]`.
- **Faster guards.** In `guards.py`, `GUARD_SPEED = 2` becomes `GUARD_SPEEDS = [2, 3]`, and each
  `GUARD_SPEED` in `move_guards()` becomes `GUARD_SPEEDS[game.mission_number]`.
- **Show the mission.** `draw_label("Mission 2", ...)` in a corner of the dungeon, **after**
  `draw_fog(...)` (or the fog hides it!).
- **The tiles of the palace** (from H1). In `level.py`, `floor_image` becomes a list of
  2 pictures, `floor_images = [..., ...]`, and `draw_level()` uses
  `floor_images[game.mission_number]`. Same idea for the wall.
- **The story follows your choice.** The text of mission 2 can change with the ending of
  mission 1 (`THE_VICTORY_NUMBER`). Ending 3 ("he gives you another chance") is a good start:
  `"This is your last chance, Weaver."`
- **A choice in mission 2 too**, with its own endings (and their pictures).
- **A new song for the loom**: a second Suno song, with its own `LOOM_BPM` and `MUSIC_START`
  (lists again!). Its first beat must be measured with ffmpeg, like for the first song (see the
  commit `feat: add the weaving mini-game`).
- **Docs.** Update the screen flow in `CLAUDE.md` (TITLE → MISSION → ...) with mission 2.

**Done when:** you can play the whole game twice in a row (mission 1, mission 2, the end), and
once losing in mission 2 and winning it on the second try. **Commit:**
`feat: polish mission 2`.

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
