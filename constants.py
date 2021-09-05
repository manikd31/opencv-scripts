# Directories to use as default path-in and path-out
MODEL_BASE_PATH = r"C:/Users/Manik/Desktop"
TEST_PATH_IN = r"C:/Users/Manik/Desktop/test_CV_videos"
TEST_PATH_OUT = r"C:/Users/Manik/Desktop/test_CV_videos"
TEST_FILE_NAME = "video.mp4"
TEST_TARGET_FPS = 4

# Video extension
VIDEO_EXT = ".mp4"

# VideoWriter "out" four-char code
FOURCC = 0x7634706d

# VideoCapture properties
PROP_ID_WIDTH = 3
PROP_ID_HEIGHT = 4
PROP_ID_FPS = 5
PROP_ID_FRAME_COUNT = 7

# BGR codes for basic colors
STD_COLORS = {
    'Black': (0, 0, 0),
    'Blue': (255, 0, 0),
    'Cyan': (255, 255, 0),
    'Green': (0, 255, 0),
    'Pink': (255, 0, 255),
    'Red': (0, 0, 255),
    'White': (255, 255, 255),
    'Yellow': (0, 255, 255)
}

# Standard video resolutions
STD_DIMENSIONS = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
}

# FPS values
FPS16 = 16.0
FPS24 = 24.0
FPS30 = 30.0

# Saved trained models for different data-sets
DATASETS = {
    "ASL": 'my_sign_model',
    "MNIST": 'my_aug_model'
}

# Alphabets associated with ASL model predictions (without J and Z)
INT2LAB = {
    0: 'A',
    1: 'B',
    2: 'C',
    3: 'D',
    4: 'E',
    5: 'F',
    6: 'G',
    7: 'H',
    8: 'I',
    9: 'K',
    10: 'L',
    11: 'M',
    12: 'N',
    13: 'O',
    14: 'P',
    15: 'Q',
    16: 'R',
    17: 'S',
    18: 'T',
    19: 'U',
    20: 'V',
    21: 'W',
    22: 'X',
    23: 'Y'
}
