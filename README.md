# Spacexplorer

Spacexplorer is a simple 2D space exploration game built with Python and Pygame.

## Overview

Explore a procedurally generated space world, collect resources, avoid hazards, and upgrade your ship. The game includes:

- Main gameplay loop with world generation and ship controls
- Pause menu and upgrade system
- Background music and sound effects
- Modular Python code in `src/`

## Requirements

- Python 3.8 or newer
- `pygame-ce` (listed in `requirements.txt`)

## Setup

1. Clone or download the repository.
2. Open a terminal in the repository root:

```powershell
cd C:\Users\Uživatel\Documents\GitHub\Spacexplorer
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

If the installation fails, install Pygame CE directly:

```powershell
pip install pygame-ce
```

## Running the game

From the repository root, run either:

```powershell
python src/main.py
```

or:

```powershell
python -m src.main
```

To run the test grounds scene:

```powershell
python src/test_grounds.py  ----- test grounds are not completed with all of the physics functions from the main game -------
From the repository root, the recommended (preferred) way is to run the package as a module
because it preserves package-relative imports:

```powershell
python -m src.main
```

Alternatively you can run the script directly:

```powershell
python src/main.py
```

To run the test grounds scene, recommended module form:

```powershell
python -m src.test_grounds
```

Or as a script:

```powershell
python src/test_grounds.py
```
```

## Controls

### Main game
- `W` - thrust forward
- `A` / `D` - rotate the ship
- `TAB` - open/close upgrade menu
- `ESC` - pause the game
- `UP` / `DOWN` arrows - navigate menus

### Test grounds
- `W` - thrust forward
- `A` / `D` - rotate the ship
- `T` - cycle spawnable objects
- `S` - spawn the selected object at position `(0, 0)`
- `C` - clear all spawned objects

## Project structure

- `src/main.py` - game loop and state management
- `src/utils.py` - image loading, sound helper functions, audio management
- `src/menu.py` - main menu, pause menu, upgrade menu
- `src/engine.py` - world simulation, camera, minimap, physics
- `src/entities.py` - ship, enemies, asteroids, planets, and game entities
- `src/space.py` - additional background and space-specific classes
- `src/img/` - images and sound assets
- `docs/` - documentation sources

## Notes

- Music is played during gameplay and stops when the game enters pause or menu screens. (kind of wrong, i just randomly choose another track to play from the beginning on unpause)
- The project is still under development, so features and controls may change.

## Music credits

Background music tracks are included in `src/img/sound/` and credited to their creators below:

- `Lost Souls`, `Cosmos` — Introspektro
- `Offworld` — Downtown Binary
- `Allude` — Voyage
- `Transition Phase` — Release Topic
- `Decay` — Lucy in Disguise

## Acknowledgements

This README was generated with assistance from an AI tool. (sorry not sorry tohle se mi uz nechce delat)

