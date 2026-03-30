# Spacexplorer

Jednoduchá space exploration hra ve 2D

### requirements:
- Python 3.8+
- Pygame-ce (obsaženo v `requirements.txt`)

### Setup:

1. Stáhni repo a jdi do složky:

cd Spacexplorer


2. Nainstalovat dependence:

pip install -r requirements.txt


Pokud nefunguje:

pip install pygame-ce


### Spuštění:

V main game:

python src/main.py


V test_grounds (lze spawnovat objekty):

python src/test_grounds.py


## Ovládání

**Hlavní hra:**
- `W` - dopředu
- `A` / `D` - otáčí lodí

**Test grounds:**
- `W` - dopředu
- `A` / `D` - otáčí lodi
- `T` - switch mezi objekty k spawnování (je vidět v top middle který je vybarný)
- `S` - spawn objektu na pozici (0,0)
- `C` - smaže všechny spawnnuté objekty


Hra je ještě v průběhu vývoje.

