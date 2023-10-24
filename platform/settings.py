from itertools import chain

WIDTH = 360
HEIGHT = 480
FPS = 60
FONT_NAME = 'arial'
HS_FILE = 'highscore.txt'
SPRITESHEET = 'spritesheet_jumper.png'
PLAYER_FILE = 'player_moves.csv'

MAX_TIME_BETWEEN_NOTES = 500

#patterns
# PATTERNS = [
#     [60, 64, 67],
#     [57],
#     [67, 64, 60]
#     ]


# TRANSPOSE_CONSTANT = -5
# NOTE_DIVIDING_LEFT_AND_RIGHT_HANDS = 60 + TRANSPOSE_CONSTANT
# PATTERNS = [[e + TRANSPOSE_CONSTANT for e in pattern] for pattern in PATTERNS]

# print(PATTERNS)

# AVAILABLE_NOTES = list(chain.from_iterable(PATTERNS))

# PLAYER_ACC = 1

JUMP_VEL = 2

PLAYER_FRICTION = -.12
PLAYER_GRAV = .1


BOOST_POWER = 10
POW_SPAWN_PCT = 7



PLATFORM_LIST = [
    (0, HEIGHT - 60),
    (WIDTH / 2 - 50, HEIGHT - 200),
    (0, HEIGHT - 350),
    (WIDTH / 2 + 50, HEIGHT - 350),
]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)
BGCOLOR = LIGHTBLUE
CAFE5_PURPLE = (255, 0, 255)


TITLE = "CAFE 5"