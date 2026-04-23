# Kid Game — Open Day Booth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build two standalone pygame booth games — one for 8–12 year olds and one for 13–17 year olds — where attendees write a short line of Python and watch a Mario-style character run across the screen jumping over holes.

**Architecture:** Two fully independent folders (`kid_game/`, `teen_game/`), each with a self-contained `main.py`. No shared code. Pure functions are extracted and covered by pytest. Everything else is tested manually by running the game.

**Tech Stack:** Python 3, pygame, pytest

---

## File Map

| File | Responsibility |
|------|---------------|
| `kid_game/main.py` | Full engine: constants, state dict, `reset()`, `draw()`, `update()`, `draw_overlay()`, `main()` |
| `kid_game/solution.py` | Attendee edits: `hole_positions = []` |
| `kid_game/solution_answer.py` | Booth helper reference answer |
| `teen_game/main.py` | Same engine + `jump()` function + marked coding block; holes hardcoded |
| `teen_game/main_answer.py` | Booth helper reference answer |
| `tests/test_logic.py` | Pure-function unit tests (no pygame) |

---

## Task 1: Project Setup

**Files:**
- Create: `kid_game/` directory
- Create: `teen_game/` directory
- Create: `tests/` directory
- Create: `tests/__init__.py`

- [ ] **Step 1: Create directories**

```bash
cd /home/alwaleed/projects/AUBM/kidgame
mkdir -p kid_game teen_game tests
touch tests/__init__.py
```

- [ ] **Step 2: Install pygame and pytest**

```bash
pip install pygame pytest
```

Expected output includes: `Successfully installed pygame-...`

- [ ] **Step 3: Verify pygame works**

```bash
python -c "import pygame; print(pygame.version.ver)"
```

Expected: prints a version like `2.x.x`

- [ ] **Step 4: Commit**

```bash
git init
git add tests/__init__.py
git commit -m "feat: initial project scaffold"
```

---

## Task 2: Pure Logic Tests (TDD)

**Files:**
- Create: `tests/test_logic.py`

These two pure functions will be used inside both game engines. Write the tests first.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_logic.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

HOLE_W = 60

def is_over_hole(center_x, holes, hole_w=HOLE_W):
    return any(hx <= center_x <= hx + hole_w for hx in holes)

def reached_trigger(char_x, triggers, idx):
    if idx >= len(triggers):
        return False
    return char_x >= triggers[idx]


# --- is_over_hole ---

def test_over_hole_center():
    assert is_over_hole(230, [200, 400, 600]) is True

def test_over_hole_left_edge():
    assert is_over_hole(200, [200, 400, 600]) is True

def test_over_hole_right_edge():
    assert is_over_hole(260, [200, 400, 600]) is True

def test_not_over_hole_before():
    assert is_over_hole(199, [200, 400, 600]) is False

def test_not_over_hole_after():
    assert is_over_hole(261, [200, 400, 600]) is False

def test_over_hole_empty_list():
    assert is_over_hole(300, []) is False

def test_over_second_hole():
    assert is_over_hole(420, [200, 400, 600]) is True


# --- reached_trigger ---

def test_trigger_exact():
    assert reached_trigger(200, [200, 400, 600], 0) is True

def test_trigger_just_before():
    assert reached_trigger(199, [200, 400, 600], 0) is False

def test_trigger_past_end():
    assert reached_trigger(999, [200, 400, 600], 3) is False

def test_trigger_empty():
    assert reached_trigger(500, [], 0) is False
```

- [ ] **Step 2: Run — expect all FAIL**

```bash
cd /home/alwaleed/projects/AUBM/kidgame
pytest tests/test_logic.py -v
```

Expected: `NameError` — `is_over_hole` and `reached_trigger` are defined inside the test file, so they should already pass. If any fail, fix the test logic before continuing.

- [ ] **Step 3: Confirm all pass**

```bash
pytest tests/test_logic.py -v
```

Expected: all 11 tests PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_logic.py
git commit -m "test: add pure logic tests for hole detection and jump triggers"
```

---

## Task 3: `kid_game/main.py`

**Files:**
- Create: `kid_game/main.py`

This is the complete kid game engine. Read it top to bottom — it is intentionally written to be readable by a newcomer.

- [ ] **Step 1: Write `kid_game/main.py`**

```python
import pygame
import sys
import os
import random

# Load the attendee's answer (gracefully handle missing/broken file)
try:
    from solution import hole_positions
except Exception:
    hole_positions = []

# ------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------
SCREEN_W, SCREEN_H = 800, 450
FPS            = 60
GROUND_Y       = 380          # y-coordinate of the top of the ground
GROUND_H       = SCREEN_H - GROUND_Y
CHAR_W, CHAR_H = 30, 40
HAT_W,  HAT_H  = 20, 10
CHAR_START_X   = 20.0
SPEED          = 200 / FPS    # ~3.33 px/frame  →  200 px/s  →  4-second crossing
GRAVITY        = 0.5
JUMP_VEL       = -10.0
HOLE_W         = 60
TILE_W         = 40

# Colors
GREEN       = (34, 139,  34)
DARK_GREEN  = ( 0, 100,   0)
RED         = (220,  50,  50)
BROWN       = (101,  67,  33)
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
YELLOW      = (255, 215,   0)
SKY         = (135, 206, 235)

# ------------------------------------------------------------------
# GAME STATE  (single dict — no global keyword needed)
# ------------------------------------------------------------------
s = {}

def reset():
    s.update(
        char_x   = CHAR_START_X,
        char_y   = float(GROUND_Y - CHAR_H),
        vel_y    = 0.0,
        on_ground= True,
        phase    = 'waiting',   # 'waiting' | 'running' | 'won' | 'fell'
        jump_idx = 0,
        confetti = [],
        triggers = sorted(hole_positions),
    )

# ------------------------------------------------------------------
# CONFETTI
# ------------------------------------------------------------------
def spawn_confetti():
    s['confetti'] = [
        dict(
            x     = random.randint(0, SCREEN_W),
            y     = random.randint(-60, 0),
            vx    = random.uniform(-1.0, 1.0),
            vy    = random.uniform(2.0, 5.0),
            w     = random.randint(6, 12),
            h     = random.randint(4, 8),
            color = random.choice([
                (255,  60,  60),
                ( 60, 200,  60),
                ( 60, 120, 255),
                (255, 200,   0),
                (200,  60, 200),
            ]),
        )
        for _ in range(80)
    ]

# ------------------------------------------------------------------
# UPDATE  (pure game logic — no rendering)
# ------------------------------------------------------------------
def update():
    if s['phase'] != 'running':
        return

    s['char_x'] += SPEED

    # Trigger a jump when character reaches the next hole position
    triggers = s['triggers']
    idx = s['jump_idx']
    if idx < len(triggers) and s['char_x'] >= triggers[idx] and s['on_ground']:
        s['vel_y']    = JUMP_VEL
        s['on_ground'] = False
        s['jump_idx'] += 1

    # Gravity
    s['vel_y'] += GRAVITY
    s['char_y'] += s['vel_y']

    # Land only on solid ground (not over a hole)
    center_x  = s['char_x'] + CHAR_W / 2
    over_hole = any(hx <= center_x <= hx + HOLE_W for hx in hole_positions)
    if s['char_y'] + CHAR_H >= GROUND_Y and not over_hole:
        s['char_y']    = float(GROUND_Y - CHAR_H)
        s['vel_y']     = 0.0
        s['on_ground'] = True

    # Outcomes
    if s['char_y'] > SCREEN_H:
        s['phase'] = 'fell'
    elif s['char_x'] > SCREEN_W:
        s['phase'] = 'won'
        spawn_confetti()

# ------------------------------------------------------------------
# DRAW  (world layer — background, clouds, ground, character)
# ------------------------------------------------------------------
def draw(screen, bg):
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(SKY)

    # Clouds
    for rx, ry, rw, rh in [(100, 60, 120, 50), (140, 45, 80, 40),
                            (500, 80, 100, 40), (540, 65,  70, 35)]:
        pygame.draw.ellipse(screen, WHITE, (rx, ry, rw, rh))

    # Ground tiles (skip positions covered by holes)
    tx = 0
    while tx < SCREEN_W:
        if not any(hx <= tx < hx + HOLE_W for hx in hole_positions):
            pygame.draw.rect(screen, GREEN,      (tx, GROUND_Y,     TILE_W, GROUND_H))
            pygame.draw.rect(screen, DARK_GREEN, (tx, GROUND_Y,     TILE_W, 8))
        tx += TILE_W

    # Character body + hat + eyes
    cx, cy = int(s['char_x']), int(s['char_y'])
    pygame.draw.rect(screen, RED,   (cx,                        cy,          CHAR_W, CHAR_H))
    pygame.draw.rect(screen, BROWN, (cx + (CHAR_W - HAT_W)//2, cy - HAT_H,  HAT_W,  HAT_H))
    pygame.draw.circle(screen, WHITE, (cx +  8, cy + 12), 5)
    pygame.draw.circle(screen, WHITE, (cx + 22, cy + 12), 5)
    pygame.draw.circle(screen, BLACK, (cx +  9, cy + 12), 2)
    pygame.draw.circle(screen, BLACK, (cx + 23, cy + 12), 2)

# ------------------------------------------------------------------
# DRAW OVERLAY  (phase-specific UI on top of the world)
# ------------------------------------------------------------------
def draw_overlay(screen, font, big_font):
    phase = s['phase']
    W, H  = SCREEN_W, SCREEN_H

    if phase == 'waiting':
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 110))
        screen.blit(ov, (0, 0))
        t = big_font.render("Press ENTER to run!", True, WHITE)
        screen.blit(t, (W // 2 - t.get_width() // 2, H // 2 - t.get_height() // 2))

    elif phase == 'won':
        for p in s['confetti']:
            p['x'] += p['vx']
            p['y'] += p['vy']
            pygame.draw.rect(screen, p['color'],
                             (int(p['x']), int(p['y']), p['w'], p['h']))
        t   = big_font.render("You made it!", True, YELLOW)
        sub = font.render("Press R to run again   |   Q to quit", True, WHITE)
        screen.blit(t,   (W // 2 - t.get_width()   // 2, 140))
        screen.blit(sub, (W // 2 - sub.get_width() // 2, 210))

    elif phase == 'fell':
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        screen.blit(ov, (0, 0))
        t   = big_font.render("You fell!", True, (220, 60, 60))
        sub = font.render("Press R to run again   |   Q to quit", True, WHITE)
        screen.blit(t,   (W // 2 - t.get_width()   // 2, H // 2 - 40))
        screen.blit(sub, (W // 2 - sub.get_width() // 2, H // 2 + 20))

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Coding Game — Junior Edition")
    clock    = pygame.time.Clock()
    font     = pygame.font.SysFont('Arial', 24)
    big_font = pygame.font.SysFont('Arial', 52, bold=True)

    bg      = None
    bg_path = os.path.join(os.path.dirname(__file__), '..', 'campus.jpg')
    if os.path.exists(bg_path):
        bg = pygame.transform.scale(
            pygame.image.load(bg_path), (SCREEN_W, SCREEN_H)
        )

    reset()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and s['phase'] == 'waiting':
                    s['phase'] = 'running'
                elif event.key == pygame.K_r and s['phase'] in ('won', 'fell'):
                    reset()
                elif event.key == pygame.K_q and s['phase'] in ('won', 'fell'):
                    pygame.quit()
                    sys.exit()

        update()
        draw(screen, bg)
        draw_overlay(screen, font, big_font)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run the kid game manually — visual check**

```bash
cd /home/alwaleed/projects/AUBM/kidgame/kid_game
python main.py
```

Checklist:
- [ ] Window opens (800×450), sky/campus background visible
- [ ] Clouds appear
- [ ] Full green ground (no holes yet — solution.py doesn't exist)
- [ ] Red character with hat sitting on ground at left
- [ ] Translucent dark overlay with "Press ENTER to run!" centred
- [ ] Press Enter → character runs right at a steady pace and exits screen in ~4 seconds
- [ ] "You made it!" screen appears with confetti falling
- [ ] R restarts, Q quits

- [ ] **Step 3: Commit**

```bash
cd /home/alwaleed/projects/AUBM/kidgame
git add kid_game/main.py
git commit -m "feat: kid_game engine — draw, update, overlays, game loop"
```

---

## Task 4: `kid_game/solution.py` + `kid_game/solution_answer.py`

**Files:**
- Create: `kid_game/solution.py`
- Create: `kid_game/solution_answer.py`

- [ ] **Step 1: Create `kid_game/solution.py`**

```python
# -------------------------------------------------------
#  Your job: fill in the list of hole positions!
#
#  Each number is an x position on the screen.
#  The screen is 800 pixels wide.
#  The character will jump at each position you list.
#
#  Try adding:  200, 400, 600
# -------------------------------------------------------

hole_positions = [  ]   # <-- add numbers here, then run main.py
```

- [ ] **Step 2: Create `kid_game/solution_answer.py`**

```python
# Booth helper reference — correct answer

hole_positions = [200, 400, 600]
```

- [ ] **Step 3: Test with the answer — visual check**

```bash
cd /home/alwaleed/projects/AUBM/kidgame/kid_game
# Temporarily rename to use the answer
cp solution_answer.py solution.py
python main.py
```

Checklist:
- [ ] Three gaps visible in the ground at x ≈ 200, 400, 600
- [ ] Press Enter → character jumps at each gap and clears all three
- [ ] "You made it!" + confetti

- [ ] **Step 4: Restore blank solution.py**

```bash
cd /home/alwaleed/projects/AUBM/kidgame/kid_game
cat > solution.py << 'EOF'
# -------------------------------------------------------
#  Your job: fill in the list of hole positions!
#
#  Each number is an x position on the screen.
#  The screen is 800 pixels wide.
#  The character will jump at each position you list.
#
#  Try adding:  200, 400, 600
# -------------------------------------------------------

hole_positions = [  ]   # <-- add numbers here, then run main.py
EOF
```

- [ ] **Step 5: Test with empty solution — character should run with no holes**

```bash
cd /home/alwaleed/projects/AUBM/kidgame/kid_game
python main.py
```

Expected: no holes, character runs to end, wins.

- [ ] **Step 6: Commit**

```bash
cd /home/alwaleed/projects/AUBM/kidgame
git add kid_game/solution.py kid_game/solution_answer.py
git commit -m "feat: kid_game attendee solution file and reference answer"
```

---

## Task 5: `teen_game/main.py`

**Files:**
- Create: `teen_game/main.py`

Same engine as the kid game with three differences:
1. Holes are **hardcoded** at `[200, 400, 600]` — attendee does not define them
2. `jump()` function is defined near the top and clearly visible
3. A marked coding block using a `for x in range(...)` loop calls `jump(x)`

- [ ] **Step 1: Write `teen_game/main.py`**

```python
import pygame
import sys
import os
import random

# ------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------
SCREEN_W, SCREEN_H = 800, 450
FPS            = 60
GROUND_Y       = 380
GROUND_H       = SCREEN_H - GROUND_Y
CHAR_W, CHAR_H = 30, 40
HAT_W,  HAT_H  = 20, 10
CHAR_START_X   = 20.0
SPEED          = 200 / FPS    # ~3.33 px/frame  →  4-second crossing
GRAVITY        = 0.5
JUMP_VEL       = -10.0
HOLE_W         = 60
TILE_W         = 40
HOLES          = [200, 400, 600]   # fixed — your job is to jump over them!

# Colors
GREEN       = (34, 139,  34)
DARK_GREEN  = ( 0, 100,   0)
RED         = (220,  50,  50)
BROWN       = (101,  67,  33)
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
YELLOW      = (255, 215,   0)
SKY         = (135, 206, 235)

# ------------------------------------------------------------------
# JUMP  (read this before you write your code below!)
# ------------------------------------------------------------------
jump_queue = []

def jump(x):
    """Schedule a jump when the character reaches position x."""
    jump_queue.append(x)


# ==================================================================
#  YOUR CODE HERE
#
#  The screen is 800 pixels wide.
#  Holes are at x = 200, 400, 600.
#
#  Use range() to generate the x positions you want to jump at,
#  then call jump(x) for each one.
#
#  Hint:  range(start, stop, step)
# ==================================================================

try:
    for x in range(_______, _______, _______):
        jump(x)
except Exception:
    pass   # fill in the blanks above!

# ==================================================================


# ------------------------------------------------------------------
# GAME STATE
# ------------------------------------------------------------------
s = {}

def reset():
    s.update(
        char_x    = CHAR_START_X,
        char_y    = float(GROUND_Y - CHAR_H),
        vel_y     = 0.0,
        on_ground = True,
        phase     = 'waiting',
        jump_idx  = 0,
        confetti  = [],
        triggers  = sorted(set(jump_queue)),
    )

# ------------------------------------------------------------------
# CONFETTI
# ------------------------------------------------------------------
def spawn_confetti():
    s['confetti'] = [
        dict(
            x     = random.randint(0, SCREEN_W),
            y     = random.randint(-60, 0),
            vx    = random.uniform(-1.0, 1.0),
            vy    = random.uniform(2.0, 5.0),
            w     = random.randint(6, 12),
            h     = random.randint(4, 8),
            color = random.choice([
                (255,  60,  60),
                ( 60, 200,  60),
                ( 60, 120, 255),
                (255, 200,   0),
                (200,  60, 200),
            ]),
        )
        for _ in range(80)
    ]

# ------------------------------------------------------------------
# UPDATE
# ------------------------------------------------------------------
def update():
    if s['phase'] != 'running':
        return

    s['char_x'] += SPEED

    # Trigger a jump when character reaches the next scheduled position
    triggers = s['triggers']
    idx = s['jump_idx']
    if idx < len(triggers) and s['char_x'] >= triggers[idx] and s['on_ground']:
        s['vel_y']     = JUMP_VEL
        s['on_ground'] = False
        s['jump_idx'] += 1

    # Gravity
    s['vel_y'] += GRAVITY
    s['char_y'] += s['vel_y']

    # Land only on solid ground (not over a hole)
    center_x  = s['char_x'] + CHAR_W / 2
    over_hole = any(hx <= center_x <= hx + HOLE_W for hx in HOLES)
    if s['char_y'] + CHAR_H >= GROUND_Y and not over_hole:
        s['char_y']    = float(GROUND_Y - CHAR_H)
        s['vel_y']     = 0.0
        s['on_ground'] = True

    if s['char_y'] > SCREEN_H:
        s['phase'] = 'fell'
    elif s['char_x'] > SCREEN_W:
        s['phase'] = 'won'
        spawn_confetti()

# ------------------------------------------------------------------
# DRAW
# ------------------------------------------------------------------
def draw(screen, bg):
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(SKY)

    for rx, ry, rw, rh in [(100, 60, 120, 50), (140, 45, 80, 40),
                            (500, 80, 100, 40), (540, 65,  70, 35)]:
        pygame.draw.ellipse(screen, WHITE, (rx, ry, rw, rh))

    tx = 0
    while tx < SCREEN_W:
        if not any(hx <= tx < hx + HOLE_W for hx in HOLES):
            pygame.draw.rect(screen, GREEN,      (tx, GROUND_Y, TILE_W, GROUND_H))
            pygame.draw.rect(screen, DARK_GREEN, (tx, GROUND_Y, TILE_W, 8))
        tx += TILE_W

    cx, cy = int(s['char_x']), int(s['char_y'])
    pygame.draw.rect(screen, RED,   (cx,                        cy,         CHAR_W, CHAR_H))
    pygame.draw.rect(screen, BROWN, (cx + (CHAR_W - HAT_W)//2, cy - HAT_H, HAT_W,  HAT_H))
    pygame.draw.circle(screen, WHITE, (cx +  8, cy + 12), 5)
    pygame.draw.circle(screen, WHITE, (cx + 22, cy + 12), 5)
    pygame.draw.circle(screen, BLACK, (cx +  9, cy + 12), 2)
    pygame.draw.circle(screen, BLACK, (cx + 23, cy + 12), 2)

# ------------------------------------------------------------------
# DRAW OVERLAY
# ------------------------------------------------------------------
def draw_overlay(screen, font, big_font):
    phase = s['phase']
    W, H  = SCREEN_W, SCREEN_H

    if phase == 'waiting':
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 110))
        screen.blit(ov, (0, 0))
        t = big_font.render("Press ENTER to run!", True, WHITE)
        screen.blit(t, (W // 2 - t.get_width() // 2, H // 2 - t.get_height() // 2))

    elif phase == 'won':
        for p in s['confetti']:
            p['x'] += p['vx']
            p['y'] += p['vy']
            pygame.draw.rect(screen, p['color'],
                             (int(p['x']), int(p['y']), p['w'], p['h']))
        t   = big_font.render("You made it!", True, YELLOW)
        sub = font.render("Press R to run again   |   Q to quit", True, WHITE)
        screen.blit(t,   (W // 2 - t.get_width()   // 2, 140))
        screen.blit(sub, (W // 2 - sub.get_width() // 2, 210))

    elif phase == 'fell':
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        screen.blit(ov, (0, 0))
        t   = big_font.render("You fell!", True, (220, 60, 60))
        sub = font.render("Press R to run again   |   Q to quit", True, WHITE)
        screen.blit(t,   (W // 2 - t.get_width()   // 2, H // 2 - 40))
        screen.blit(sub, (W // 2 - sub.get_width() // 2, H // 2 + 20))

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Coding Game — Senior Edition")
    clock    = pygame.time.Clock()
    font     = pygame.font.SysFont('Arial', 24)
    big_font = pygame.font.SysFont('Arial', 52, bold=True)

    bg      = None
    bg_path = os.path.join(os.path.dirname(__file__), '..', 'campus.jpg')
    if os.path.exists(bg_path):
        bg = pygame.transform.scale(
            pygame.image.load(bg_path), (SCREEN_W, SCREEN_H)
        )

    reset()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and s['phase'] == 'waiting':
                    s['phase'] = 'running'
                elif event.key == pygame.K_r and s['phase'] in ('won', 'fell'):
                    reset()
                elif event.key == pygame.K_q and s['phase'] in ('won', 'fell'):
                    pygame.quit()
                    sys.exit()

        update()
        draw(screen, bg)
        draw_overlay(screen, font, big_font)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run with blank range — character should fall**

```bash
cd /home/alwaleed/projects/AUBM/kidgame/teen_game
python main.py
```

Expected:
- [ ] Three gaps in the ground visible at x ≈ 200, 400, 600
- [ ] Press Enter → character runs and falls into the first hole at x=200
- [ ] "You fell!" dark overlay + prompt to restart

- [ ] **Step 3: Temporarily fill in the correct answer and verify win**

Edit the `for x in range(...)` line in `teen_game/main.py`:

```python
for x in range(200, 800, 200):
    jump(x)
```

Run again:

```bash
python main.py
```

Expected: character jumps at x=200, 400, 600 and wins. Confetti falls.

- [ ] **Step 4: Restore the blank range**

```python
try:
    for x in range(_______, _______, _______):
        jump(x)
except Exception:
    pass   # fill in the blanks above!
```

- [ ] **Step 5: Commit**

```bash
cd /home/alwaleed/projects/AUBM/kidgame
git add teen_game/main.py
git commit -m "feat: teen_game engine with jump() function and coding task block"
```

---

## Task 6: `teen_game/main_answer.py`

**Files:**
- Create: `teen_game/main_answer.py`

- [ ] **Step 1: Copy main.py and fill in the correct answer**

```bash
cp /home/alwaleed/projects/AUBM/kidgame/teen_game/main.py \
   /home/alwaleed/projects/AUBM/kidgame/teen_game/main_answer.py
```

- [ ] **Step 2: Edit the coding block in `teen_game/main_answer.py`**

Replace:
```python
try:
    for x in range(_______, _______, _______):
        jump(x)
except Exception:
    pass   # fill in the blanks above!
```

With:
```python
for x in range(200, 800, 200):
    jump(x)
```

- [ ] **Step 3: Run the answer file to confirm it wins**

```bash
cd /home/alwaleed/projects/AUBM/kidgame/teen_game
python main_answer.py
```

Expected: three visible holes, character jumps over all three, confetti on win.

- [ ] **Step 4: Commit**

```bash
cd /home/alwaleed/projects/AUBM/kidgame
git add teen_game/main_answer.py
git commit -m "feat: teen_game reference answer for booth helpers"
```

---

## Task 7: Final Visual QA Checklist

Run both games end-to-end and verify the complete experience.

- [ ] **Kid game — empty solution**
  - `cd kid_game && python main.py`
  - Translucent overlay on open ✓
  - No holes (empty list) ✓
  - Character runs to end and wins ✓
  - Confetti falls on win screen ✓
  - R restarts, Q quits ✓

- [ ] **Kid game — correct solution**
  - Copy `solution_answer.py` → `solution.py`
  - Three holes visible ✓
  - Character jumps over all three ✓
  - Restore blank `solution.py` afterward ✓

- [ ] **Teen game — blank range (default)**
  - `cd teen_game && python main.py`
  - Three holes visible ✓
  - Character falls at first hole ✓
  - Dark overlay on "You fell!" ✓
  - R restarts ✓

- [ ] **Teen game — correct answer**
  - Fill in `range(200, 800, 200)` ✓
  - Character jumps all three ✓
  - Confetti on win ✓
  - Restore blank range ✓

- [ ] **Campus background** (once `campus.jpg` is in place)
  - Copy your campus photo: `cp /path/to/your/photo.jpg /home/alwaleed/projects/AUBM/kidgame/campus.jpg`
  - Run either game — background should show the campus photo instead of solid sky

- [ ] **Final commit**

```bash
cd /home/alwaleed/projects/AUBM/kidgame
git add -A
git commit -m "chore: final QA pass — both games complete and verified"
```

---

## Booth Quick-Reference

| Action | Command |
|--------|---------|
| Run kid game | `cd kid_game && python main.py` |
| Run teen game | `cd teen_game && python main.py` |
| Reset for next attendee | Close window, run `python main.py` again |
| Show correct answer (kid) | `cp solution_answer.py solution.py` then run |
| Show correct answer (teen) | Run `python main_answer.py` |
