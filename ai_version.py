import pygame
import random
import os

# ============================
# MATCH-3 (Candy Crush style)
# Smooth swap + fall animations
# ============================
pygame.init()

# -------- Settings --------
GRID = 6
TILE = 80
MARGIN = 8
FPS = 60


ANIM_DURATION = 600  # ms for tile swap animation
FALL_DURATION = 900  # ms for tiles falling into place
SHAKE_DURATION = 220
SHAKE_STRENGTH = 6  # pixels
SHRINK_DURATION = 150  # ms for tile shrink when clearing


# Screen size
BOARD_W = GRID * TILE + (GRID + 1) * MARGIN
UI_H = 70
W, H = BOARD_W, BOARD_W + UI_H


screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Emoji Match-3")


clock = pygame.time.Clock()
ui_font = pygame.font.SysFont(None, 32)


HIGHLIGHT = (255, 255, 255)


# -------- Load images --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))




def load_image(name, size=None, alpha=True):
    path = os.path.join(BASE_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {name}")
    img = pygame.image.load(path)
    img = img.convert_alpha() if alpha else img.convert()
    if size:
        img = pygame.transform.smoothscale(img, size)
    return img




board_bg = load_image("img/board.png", size=(BOARD_W, BOARD_W), alpha=False)


tile_size = (TILE - 24, TILE - 24)
EMOJIS = [
    load_image("img/emoji1.png", tile_size),
    load_image("img/emoji2.png", tile_size),
    load_image("img/emoji3.png", tile_size),
    load_image("img/emoji4.png", tile_size),
    load_image("img/emoji5.png", tile_size),
]
N_TYPES = len(EMOJIS)




# -------- Helpers --------
def tile_rect(r, c):
    x = MARGIN + c * (TILE + MARGIN)
    y = MARGIN + r * (TILE + MARGIN)
    return pygame.Rect(x, y, TILE, TILE)




def pixel_to_cell(mx, my):
    if mx < MARGIN or my < MARGIN:
        return None
    c = (mx - MARGIN) // (TILE + MARGIN)
    r = (my - MARGIN) // (TILE + MARGIN)
    if 0 <= r < GRID and 0 <= c < GRID:
        if tile_rect(r, c).collidepoint(mx, my):
            return (r, c)
    return None




def adjacent(a, b):
    r1, c1 = a
    r2, c2 = b
    return abs(r1 - r2) + abs(c1 - c2) == 1




def lerp(a, b, t):
    return a + (b - a) * t




def ease_out_cubic(t):
    return 1 - pow(1 - t, 3)




# -------- Board logic --------
def new_board():
    return [[random.randrange(N_TYPES) for _ in range(GRID)] for _ in range(GRID)]


def find_matches(board):
    matches = set()

    # horizontal
    for r in range(GRID):
        c = 0
        while c < GRID - 2:
            val = board[r][c]
            run = 1
            while c + run < GRID and board[r][c + run] == val:
                run += 1
            if val is not None and run >= 3:
                for i in range(run):
                    matches.add((r, c + i))
            c += run


    # vertical
    for c in range(GRID):
        r = 0
        while r < GRID - 2:
            val = board[r][c]
            run = 1
            while r + run < GRID and board[r + run][c] == val:
                run += 1
            if val is not None and run >= 3:
                for i in range(run):
                    matches.add((r + i, c))
            r += run


    return matches




def clear_matches(board, matches):
    for r, c in matches:
        board[r][c] = None


def make_shrink_animation(board, matches):
    tiles = []
    for (r, c) in matches:
        tiles.append({"r": r, "c": c, "val": board[r][c]})
    anim = {
        "type": "shrink",
        "tiles": tiles,
        "matches": set(matches),
        "board_before": [row[:] for row in board],
        "duration": SHRINK_DURATION,
    }
    return anim


def drop_and_fill(board):
    for c in range(GRID):
        stack = []
        for r in range(GRID - 1, -1, -1):
            if board[r][c] is not None:
                stack.append(board[r][c])


        r = GRID - 1
        for val in stack:
            board[r][c] = val
            r -= 1


        while r >= 0:
            board[r][c] = random.randrange(N_TYPES)
            r -= 1




def swap(board, a, b):
    r1, c1 = a
    r2, c2 = b
    board[r1][c1], board[r2][c2] = board[r2][c2], board[r1][c1]




def resolve_cascades(board):
    total = 0
    while True:
        matches = find_matches(board)
        if not matches:
            break
        total += len(matches)
        clear_matches(board, matches)
        drop_and_fill(board)
    return total




def make_start_stable(board):
    # ensure initial board has no immediate matches
    while True:
        matches = find_matches(board)
        if not matches:
            break
        clear_matches(board, matches)
        drop_and_fill(board)




def compute_fall_animation(board, matches):
    board_before = [row[:] for row in board]


    # clear matches
    for r, c in matches:
        board_before[r][c] = None


    board_after = [row[:] for row in board_before]
    tiles = []


    for c in range(GRID):
        existing = []


        # collect existing tiles bottom-up
        for r in range(GRID - 1, -1, -1):
            val = board_before[r][c]
            if val is not None:
                existing.append((r, val))


        dest_r = GRID - 1


        # drop existing tiles
        for start_r, val in existing:
            board_after[dest_r][c] = val
            tiles.append({
                "start_r": start_r,
                "end_r": dest_r,
                "c": c,
                "val": val
            })
            dest_r -= 1


        # spawn new tiles above the board
        num_new = dest_r + 1
        for i in range(num_new):
            val = random.randrange(N_TYPES)
            start_r = -(num_new - i)
            end_r = i
            board_after[end_r][c] = val
            tiles.append({
                "start_r": start_r,
                "end_r": end_r,
                "c": c,
                "val": val
            })


    anim = {
        "type": "fall",
        "tiles": tiles,
        "board_before": board_before,
        "board_after": board_after,
        "duration": FALL_DURATION,
    }


    return anim, len(matches), board_after






# -------- Drawing / animation helpers --------
def draw(board, selected, score, message, anim):
    screen.fill((30, 30, 30))
    screen.blit(board_bg, (0, 0))


    # draw static board base depending on animation type
    moving_cells = set()
    if anim and anim.get("type") == "swap":
        a, b = anim["cells"]
        moving_cells.add(a)
        moving_cells.add(b)
    elif anim and anim.get("type") == "fall":
        # moving tiles list
        for t in anim["tiles"]:
            sr = t["start_r"]
            c = t["c"]
            # if start is within board, mark that cell as moving (so we don't draw static tile there)
            if 0 <= sr < GRID:
                moving_cells.add((sr, c))
    elif anim and anim.get("type") == "shrink":
        # matched tiles shrink so treat them as moving (don't draw static)
        for t in anim["tiles"]:
            moving_cells.add((t["r"], t["c"]))


    # draw static tiles (board state passed in should be current board or board_before)
    for r in range(GRID):
        for c in range(GRID):
            if (r, c) in moving_cells:
                continue
            val = board[r][c]
            if val is None:
                continue
            rect = tile_rect(r, c)
            center = rect.center
            img = EMOJIS[val]
            screen.blit(img, img.get_rect(center=center))


    # draw animated elements
    if anim:
        p = ease_out_cubic(anim.get("progress", 1.0))
        if anim["type"] == "swap":
            (r1, c1), (r2, c2) = anim["cells"]
            rect1 = tile_rect(r1, c1)
            rect2 = tile_rect(r2, c2)
            x1, y1 = rect1.center
            x2, y2 = rect2.center
            x_a = lerp(x1, x2, p)
            y_a = lerp(y1, y2, p)
            x_b = lerp(x2, x1, p)
            y_b = lerp(y2, y1, p)
            v1 = board[r2][c2]  # note: board may have been swapped already when anim started; we draw actual moving images by values passed into anim if provided
            v2 = board[r1][c1]
            # If anim provided explicit values, prefer them:
            if "vals" in anim:
                v1, v2 = anim["vals"]
            screen.blit(EMOJIS[v1], EMOJIS[v1].get_rect(center=(x_a, y_a)))
            screen.blit(EMOJIS[v2], EMOJIS[v2].get_rect(center=(x_b, y_b)))


        elif anim["type"] == "fall":
            board_before = anim["board_before"]
            for t in anim["tiles"]:
                sr = t["start_r"]
                er = t["end_r"]
                c = t["c"]
                val = t["val"]
                start_y = MARGIN + sr * (TILE + MARGIN)
                end_y = MARGIN + er * (TILE + MARGIN)
                # start_r may be negative (above board)
                start_y = MARGIN + sr * (TILE + MARGIN)
                x = MARGIN + c * (TILE + MARGIN) + TILE // 2
                y = lerp(start_y + TILE // 2, end_y + TILE // 2, p)
                screen.blit(EMOJIS[val], EMOJIS[val].get_rect(center=(x, y)))
        elif anim["type"] == "shrink":
            # render matched tiles scaled down
            for t in anim["tiles"]:
                r = t["r"]; c = t["c"]; val = t["val"]
                rect = tile_rect(r, c)
                center = rect.center
                img = EMOJIS[val]
                scale = max(0.01, 1.0 - p)  # from 1.0 -> ~0.0
                w = max(1, int(img.get_width() * scale))
                h = max(1, int(img.get_height() * scale))
                img_s = pygame.transform.smoothscale(img, (w, h))
                screen.blit(img_s, img_s.get_rect(center=center))


    # selection highlight
    if selected:
        r, c = selected
        rect = tile_rect(r, c)
        pygame.draw.rect(screen, HIGHLIGHT, rect, 3)


    # UI
    pygame.draw.rect(screen, (15, 15, 15), (0, BOARD_W, W, UI_H))
    screen.blit(ui_font.render(f"Score: {score}", True, (255, 255, 255)), (12, BOARD_W + 12))
    if message:
        screen.blit(ui_font.render(message, True, (255, 200, 200)), (12, BOARD_W + 38))


    pygame.display.flip()




# ============================
# Main Game
# ============================


board = new_board()
make_start_stable(board)


selected = None
score = 0
message = ""


animating = False
anim_start = 0
anim_data = None  # will hold current animation dict (swap/fall)
swap_a = swap_b = None


running = True
while running:
    clock.tick(FPS)
    message = ""
    anim = None


    # animation progress preparation for draw()
    if animating and anim_data:
        elapsed = pygame.time.get_ticks() - anim_start
        duration = anim_data.get("duration", ANIM_DURATION)
        progress = min(1, elapsed / duration)
        anim = {"type": anim_data["type"], "progress": progress}
        if anim_data["type"] == "swap":
            anim["cells"] = anim_data["cells"]
            anim["vals"] = anim_data.get("vals")
        elif anim_data["type"] == "fall":
            anim.update({"tiles": anim_data["tiles"], "board_before": anim_data["board_before"]})
        elif anim_data["type"] == "shrink":
            # ensure shrink animations expose their tiles to draw()
            anim.update({"tiles": anim_data.get("tiles", []), "board_before": anim_data.get("board_before")})


        # complete animation
        if progress >= 1:
            # finalize based on type
            if anim_data["type"] == "swap":
                # commit swap on logical board (if not already)
                swap(board, swap_a, swap_b)
                matches = find_matches(board)
                if not matches:
                    # revert
                    swap(board, swap_a, swap_b)
                    message = "No match — move cancelled!"
                    animating = False
                    anim_data = None
                    swap_a = swap_b = None
                else:
                    # start shrink animation for matched tiles, then fall will follow
                    shrink = make_shrink_animation(board, matches)
                    shrink["cleared"] = len(matches)
                    animating = True
                    anim_start = pygame.time.get_ticks()
                    anim_data = shrink
                    swap_a = swap_b = None


            elif anim_data["type"] == "fall":
                # apply filled board
                board = anim_data["board_after"]
                score += anim_data.get("cleared", 0) * 10
                # look for further cascades
                matches = find_matches(board)
                if matches:
                    # shrink before next fall
                    shrink = make_shrink_animation(board, matches)
                    shrink["cleared"] = len(matches)
                    animating = True
                    anim_start = pygame.time.get_ticks()
                    anim_data = shrink
                else:
                    animating = False
                    anim_data = None


            elif anim_data["type"] == "shrink":
                # after shrink, remove matched tiles and start fall animation
                matches = anim_data.get("matches", set())
                clear_matches(board, matches)
                anim_new, cleared, filled = compute_fall_animation(board, matches)
                anim_new["cleared"] = cleared
                animating = True
                anim_start = pygame.time.get_ticks()
                anim_data = anim_new


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


        if event.type == pygame.MOUSEBUTTONDOWN and not animating:
            cell = pixel_to_cell(*pygame.mouse.get_pos())
            if cell is None:
                continue


            if selected is None:
                selected = cell
            else:
                if cell == selected:
                    selected = None
                    continue


                if not adjacent(selected, cell):
                    selected = cell
                    continue


                swap_a, swap_b = selected, cell
                # prepare swap animation (draw values so visuals are correct even if board isn't committed)
                v1 = board[swap_a[0]][swap_a[1]]
                v2 = board[swap_b[0]][swap_b[1]]
                anim_data = {"type": "swap", "cells": (swap_a, swap_b), "vals": (v1, v2), "duration": ANIM_DURATION}
                animating = True
                anim_start = pygame.time.get_ticks()
                selected = None


    draw(board, selected, score, message, anim)


pygame.quit()