# ICAM Hackathon 2026 — The Dream Weaver

## Requirements

- **Python 3.10 or newer** — download it from https://www.python.org/downloads/
- **pygame-ce** (Community Edition), **not** the original `pygame`.
  The game uses `pygame.image.load_animation` to play the walking GIFs, which only exists in pygame-ce.
  Both packages install under the same name (`import pygame`), so they must not be installed together.

## Install and play on Windows

> When installing Python, tick **"Add python.exe to PATH"** on the first screen of the installer.

Open **PowerShell** (or the terminal in VS Code) in the project folder, then:

```powershell
# 1. Create a virtual environment (only the first time)
py -m venv .venv

# 2. Install the dependencies (only the first time)
.venv\Scripts\python -m pip install -r requirements.txt

# 3. Launch the game
.venv\Scripts\python main.py
```

## Install and play on Mac

Open the **Terminal** (or the terminal in VS Code) in the project folder, then:

```bash
# 1. Create a virtual environment (only the first time)
python3 -m venv .venv

# 2. Install the dependencies (only the first time)
.venv/bin/python -m pip install -r requirements.txt

# 3. Launch the game
.venv/bin/python main.py
```

## Controls

| Key            | Action                                  |
| -------------- | --------------------------------------- |
| Arrow keys     | Move the player                         |
| `SPACE`        | Continue / start / play again           |
| `1`, `2`, `3`  | Choose a thread on the weaving screen   |

## Troubleshooting

**`AttributeError: module 'pygame.image' has no attribute 'load_animation'`**
The original `pygame` is installed instead of pygame-ce. Remove it and reinstall pygame-ce:

```bash
# Windows
.venv\Scripts\python -m pip uninstall -y pygame pygame-ce
.venv\Scripts\python -m pip install pygame-ce

# Mac
.venv/bin/python -m pip uninstall -y pygame pygame-ce
.venv/bin/python -m pip install pygame-ce
```

To check which one is installed, run `python -c "import pygame"`: pygame-ce prints `pygame-ce 2.x.x`.

**`'py' is not recognized` (Windows) / `command not found: python3` (Mac)**
Python is not installed, or not in the PATH. Reinstall it from python.org (on Windows, tick "Add python.exe to PATH").

**VS Code "Run" button uses the wrong Python**
Press `Ctrl+Shift+P` (Windows) / `Cmd+Shift+P` (Mac), choose **Python: Select Interpreter**, and pick the one inside `.venv`.
