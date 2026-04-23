# Open Day Coding Booth — Kid Game Design Spec
**Date:** 2026-04-23  
**Project:** `/home/alwaleed/projects/AUBM/kidgame`

---

## Overview

Two standalone pygame games for the AUBM programming club open day booth. One laptop per game. Attendees write a few lines of code, press Enter, and watch a Mario-inspired character run across the screen — jumping holes or falling in.

---

## Directory Structure

```
kidgame/
├── kid_game/
│   ├── main.py              # engine + game loop
│   ├── solution.py          # attendee edits this
│   └── solution_answer.py   # booth helper reference
│
├── teen_game/
│   ├── main.py              # engine + marked coding section
│   └── main_answer.py       # booth helper reference
│
├── campus.jpg               # university campus background photo
└── docs/
    └── superpowers/specs/
        └── 2026-04-23-kidgame-design.md
```

Each game runs with `python main.py` from its folder. No other dependencies beyond pygame.

---

## Target Audiences

| Game | Age | Laptop |
|------|-----|--------|
| `kid_game` | 8–12 | Laptop A |
| `teen_game` | 13–17 | Laptop B |

---

## Visual Design

Both games share the same visual language:

- **Background:** `campus.jpg` scaled to fill 800×450, drawn first each frame
- **Ground:** row of green rectangles (tiles) across the bottom, with gaps at hole positions
- **Character:** red rectangle (~30×40px) with a small brown rectangle on top as a hat
- **Holes:** gaps in the ground tiles where the character falls if not jumped
- **Clouds:** 2–3 static white ellipses for atmosphere

No sprite sheets. Simple pygame shapes only — readable code, Mario-inspired color palette.

---

## Game World & Physics

| Parameter | Value |
|-----------|-------|
| Screen size | 800 × 450 px |
| FPS | 60 |
| Character speed | ~3.33 px/frame (200 px/s) |
| Total run duration | 4 seconds (800px at 200px/s) |
| Hole positions | x = 200, 400, 600 |
| Jump triggers | x = 200, 400, 600 (one per second) |
| Jump arc | upward velocity for ~20 frames, then gravity; completes within 1 second |

**Gravity:** applied every frame when character is not on ground.  
**Hole detection:** if character's feet are over a hole gap and not mid-jump → character falls off screen → game over.  
**Win condition:** character reaches x = 800 without falling.

---

## Game Flow (both games)

1. Game opens showing the level (character at start, holes visible)
2. **"Press Enter to run"** translucent rectangle prompt displayed with blurred background 
3. Attendee presses Enter → animation plays out once
4. Result screen: **"You made it!"** with celebratory effects like confetti falling of the same quality as the game, or **"You fell!"** with minimal effects of misfortune
5. **"Press R to run again | Q to quit"** prompt

---

## Coding Task

### Kid Game (8–12) — `kid_game/solution.py`

Attendee edits one line:

```python
# Your job: fill in the list of hole positions to jump over!
# Each number is an x position on the screen (screen is 800px wide).
# The character will jump at each position you list.
# Try:  hole_positions = [200, 400, 600]

hole_positions = [  ]   # <-- add numbers here, then run main.py
```

The engine imports `hole_positions` from `solution.py` and places holes + jump triggers at those x values.

### Teen Game (13–17) — marked section in `teen_game/main.py`

Attendee fills in the for loop, ~2 lines:

```python
# =========================================================
# YOUR CODE HERE
# Use range() to pick x positions, then call jump(x) each time.
# The screen is 800px wide. Holes are at x = 200, 400, 600.
# =========================================================

for x in range(_______, _______, _______):
    jump(x)
```

The correct answer is `range(200, 800, 200)`.  
`jump(x)` is defined a short scroll above in the same file — 8–10 lines, clearly readable.

---

## `jump(x)` Function (teen game)

Defined near the top of `teen_game/main.py`, clearly visible:

```python
def jump(x):
    """Schedule a jump when the character reaches position x."""
    jump_queue.append(x)
```

Simple. The engine checks `jump_queue` each frame and applies upward velocity when the character's x matches.

---

## Architecture (both games)

No classes. Functions + module-level state. Readable top to bottom.

```
main.py sections (in order):
  1. Imports + constants
  2. jump(x)              ← teen game only, near top
  3. [CODING TASK BLOCK]  ← teen game only
  4. Game state variables
  5. draw()
  6. update()
  7. main loop
```

`draw()` — renders background photo, clouds, ground tiles, holes, character  
`update()` — advances character, applies gravity, triggers jumps, checks fall  
`main loop` — handles Enter/R/Q keypresses, calls update + draw each frame

---

## Booth Helper Notes

- `solution_answer.py` / `main_answer.py` contain the correct answers for helpers to reference
- Each game is fully independent — changes to one cannot break the other
- To reset for the next attendee: close and reopen the terminal, run `python main.py`
