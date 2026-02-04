import pygame
import random

# ----------------------------
# Simple Match-3 Game (Pygame)
# ----------------------------

pygame.init()

# Grid settings
GRID_SIZE = 6
TILE_SIZE = 80
MARGIN = 5
WIDTH = GRID_SIZE * (TILE_SIZE + MARGIN) + MARGIN
HEIGHT = WIDTH + 60
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Match-3")

# Colors
BG_COLOR = (30, 30, 30)
HIGHLIGHT = (255, 255, 255)

COLORS = [
    (255, 99, 132),   # pink/red
    (255, 206, 86),   # yellow
    (153, 102, 255),  # purple
    (75, 192, 192),   # teal
    (255, 159, 64)    # orange
]

FONT = pygame.font.SysFont(None, 32)


def create_board():
    return [[random.randrange(len(COLORS)) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


def draw_board(board, selected=None, score=0):
    SCREEN.fill(BG_COLOR)

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(
                MARGIN + x * (TILE_SIZE + MARGIN),
                MARGIN + y * (TILE_SIZE + MARGIN),
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.rect(SCREEN, COLORS[board[y][x]], rect)

            if selected == (y, x):
                pygame.draw.rect(SCREEN, HIGHLIGHT, rect, 3)

    score_text = FONT.render(f"Score: {score}", True, (255, 255, 255))
    SCREEN.blit(score_text, (10, HEIGHT - 45))

    pygame.display.flip()


def find_matches(board):
    matches = set()

    # Horizontal
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE - 2):
            if board[y][x] == board[y][x + 1] == board[y][x + 2]:
                matches.update({(y, x), (y, x + 1), (y, x + 2)})

    # Vertical
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE - 2):
            if board[y][x] == board[y + 1][x] == board[y + 2][x]:
                matches.update({(y, x), (y + 1, x), (y + 2, x)})

    return matches


def remove_matches(board, matches):
    for y, x in matches:
        board[y][x] = None

    for x in range(GRID_SIZE):
        column = [board[y][x] for y in range(GRID_SIZE) if board[y][x] is not None]
        missing = GRID_SIZE - len(column)
        new_column = [random.randrange(len(COLORS)) for _ in range(missing)] + column
        for y in range(GRID_SIZE):
            board[y][x] = new_column[y]


# ----------------------------
# Main game loop
# ----------------------------

board = create_board()
selected = None
score = 0
clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            x = mx // (TILE_SIZE + MARGIN)
            y = my // (TILE_SIZE + MARGIN)

            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                if selected is None:
                    selected = (y, x)
                else:
                    y1, x1 = selected
                    y2, x2 = y, x
                    board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]
                    selected = None

    matches = find_matches(board)
    if matches:
        score += len(matches)
        remove_matches(board, matches)
        pygame.time.delay(150)

    draw_board(board, selected, score)

pygame.quit()
