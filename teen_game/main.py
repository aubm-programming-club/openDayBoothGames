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
SPEED          = 200 / FPS    # ~3.33 px/frame  ->  4-second crossing
GRAVITY        = 0.5
JUMP_VEL       = -10.0
HOLE_W         = 80
TILE_W         = 40
HOLES          = [200, 400, 600]   # fixed -- your job is to jump over them!

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
    for x in range(_, _, _):
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
        t   = big_font.render("You made it!", True, BLACK)
        sub = font.render("Press R to run again   |   Q to quit", True, YELLOW)
        screen.blit(t,   (W // 2 - t.get_width()   // 2, 140))
        screen.blit(sub, (W // 2 - sub.get_width() // 2, 210))

    elif phase == 'fell':
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        screen.blit(ov, (0, 0))
        t   = big_font.render("You did well yeyeyeyeye!", True, RED)
        sub = font.render("Press R to run again   |   Q to quit", True, YELLOW)
        screen.blit(t,   (W // 2 - t.get_width()   // 2, H // 2 - 40))
        screen.blit(sub, (W // 2 - sub.get_width() // 2, H // 2 + 20))

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Coding Game — Senior Edition - claude did this bro not you (we are going to be homeless)")
    clock    = pygame.time.Clock()
    font     = pygame.font.SysFont('Arial', 24)
    big_font = pygame.font.SysFont('Arial', 52, bold=True)

    bg      = None
    base = os.path.join(os.path.dirname(__file__), '..')
    bg_path = next((os.path.join(base, f'campus{ext}')
                    for ext in ('.jpg', '.jpeg', '.png')
                    if os.path.exists(os.path.join(base, f'campus{ext}'))), '')
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
