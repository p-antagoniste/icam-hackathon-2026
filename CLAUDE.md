# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

"The Dream Weaver": a small pygame game made for the ICAM Hackathon 2026 (theme: *weaving patterns, weaving ideas, weaving communities*) by a parent and child together. `PLAN.md` holds the game design, the step-by-step MVP plan and the list of possible improvements. Check it before adding features.

The code is meant to be read and changed by a beginner, so keep that style:
- Plain module-level functions and globals: no classes, no clever abstractions.
- Small files (about 100 lines each), each with one job (the file list is at the top of `main.py`).
- `# ---------------- SECTION ----------------` headers, and comments that explain *why* in simple words.
- Named constants at the top of the file for every tunable number.

## Commands

The game requires **pygame-ce**, not the original `pygame`: `pygame.image.load_animation` (walking GIFs) only exists in pygame-ce. Both install as `import pygame`, so never install them together.

```bash
python3 -m venv .venv                          # first time only
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py                       # run the game
```

There are no tests, linter or build step. To check a screen without opening a window, render one frame headlessly and save it as an image:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -c "
import pygame, window, screens
screens.draw_title_screen()
pygame.image.save(window.screen_surface, '/tmp/frame.png')"
```

Commit messages use the conventional commit format (`feat: ...`, `fix: ...`), which a hook checks.

## Architecture

**State machine.** The game is always on exactly one screen, `game.state`. The flow is TITLE → MISSION → TRANSITION (3 s) → DUNGEON → WEAVING (3 s, then choose 1/2/3) → WIN → MISSION. Choices 2 and 3 go to DEMO, and SPACE there goes back to WEAVING. `main.py` runs the loop at 60 FPS and calls one `draw_*_screen()` function from `screens.py` per state. Each screen function switches screens itself by setting `game.state`. To add a screen:
1. add it to `game.STATES`;
2. write its `draw_*_screen()` in `screens.py`;
3. add a branch for it in the `if/elif` in `main.py`;
4. optionally, give it a sound to play when it starts in `assets.SCREEN_SOUNDS`.

**Import order matters.** `window.py` calls `pygame.init()` and opens the display. Pictures can only be `.convert()`ed once that display exists, so `assets.py` imports `window` first. `level.py`, `player.py` and `screens.py` load their pictures at import time.

**Shared state is reached through the module.** Always write `game.state` or `player.player_x`, never `from game import state`: that makes a copy that never sees changes. `LEVEL_1` is the exception. It is changed in place (picking up the key rewrites a row, and `reset_level()` does `LEVEL_1[:] = LEVEL_1_START`), so the copies imported by `player.py` and `fog.py` stay in sync. Keep changing it in place.

**Input.** `game.keys_down` holds the keys pressed *this frame* (from KEYDOWN events), for one-shot actions like SPACE or 1/2/3, so one held SPACE can't skip two screens. Only the dungeon movement uses `pygame.key.get_pressed()` (keys held down).

**Timed screens.** TRANSITION and WEAVING store their start time in a module global that is `None` until the first frame (`transition_start`, `weaving_start`). They compute a 0→1 progress from it, and set it back to `None` (or let `reset_game()` do it) so the next run starts fresh. `weaving_start` is deliberately kept when going WEAVING → DEMO → WEAVING.

**Dungeon.** The map is a list of strings: 20×18 tiles of 40 px (800×720 window). `W` wall, `.` floor, `P` start, `K` key, `D` door. The player position is the pixel center. Movement goes one pixel at a time, x and y separately, with a 28 px hitbox. `player.hits_wall()` also handles picking up the key and touching the door: with the key, touching the door switches to WEAVING. `fog.py` casts rays against `W`/`D` tiles every frame and draws the fog last.

**Messages.** Use `draw_message(lines)` from `screens.py` for text panels. It picks a font size that fits and wraps long lines. The first line is drawn as a gold title, and the last line (the key to press) blinks.

## Assets

Pictures go in `grafiki/` and load with `assets.load_sprite` (PNG with transparency), `load_animation` (GIF frames) or `load_background` (scaled to cover the window, then cropped in the center). Sound effects (`sound/*.mp3`) are loaded by name into `assets.sounds`, and the background music is in `music/`. The sources are written in comments: PixelLab for the sprites, ElevenLabs for the sounds, Suno for the music, Gemini for the title image.
