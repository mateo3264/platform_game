import pyaudio

WIDTH = 800
HEIGHT = 480
FPS = 60
FONT_NAME = 'arial'
HS_FILE = 'highscore.txt'
SPRITESHEET = 'spritesheet_jumper.png'
PLAYER_FILE = 'player_moves.csv'

MAX_TIME_BETWEEN_NOTES = 500


PLAYER_LAYER = 2
PLATFORM_LAYER = 1
POW_LAYER = 1
MOB_LAYER = 2
CLOUD_LAYER = [0, 3]

JUMP_VEL = 20

# PLAYER_FRICTION = -.12



BOOST_POWER = 40
POW_SPAWN_PCT = 7

MOB_FREQ = 5000

easy_configs = {
    'wings_range':(20, 25),
    'max_pct_pows':30,
    'min_pct_pows':10,
    
}

hard_configs = {
    'wings_range':(5, 15),
    'max_pct_pows':20,
    'min_pct_pows':5,

}

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
DARK_GRAY = (58, 67, 82)


TITLE = "CAFE 5"

AUDIO_CHUNK_SIZE = 768
AUDIO_FORMAT = pyaudio.paInt16
AUDIO_CHANNELS = 1
AUDIO_RATE = 44100





