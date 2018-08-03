OPENPOSE_DIR = '/home/il/software/openpose'
OPENPOSE_BIN_FILE_DIR = './build2/examples/openpose/'

JSON_FILE_DIR = 'json_files'
IMAGE_FILE_DIR = 'image_files'
IMAGE_WRITE_DIR = 'direction_images'

# set flag to True if you want to save images with instruction labels
SAVE_IMAGES_WITH_ANNOTATION = True

# setting flag to True will drastically slow down performance but will show actual recorded images
USE_REAL_IMAGE = False

COLOR_RED = (0, 0, 255) # BGR order
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_PURPLE = (255, 0, 255)
COLOR_LIGHT_GREEN = (0, 50, 0)
COLOR_LIGHT_RED = (0, 0, 50)
COLOR_YELLOW = (0, 255, 255)

PART_LOCATION_RADIUS = 5

CIRCLE_THICKNESS = 3
CIRCLE_RADIUS = 15

LINE_THICKNESS = 5
ERROR_LINE_THICKNESS = 3
HEAD_RATIO = 0.7

WIDTH = 1280
HEIGHT = 720

CAMERA_FLIP = True

BODY_CONNECTIONS_DICT = {
    'nose': ('neck',),
    'neck': ('right shoulder', 'left shoulder', 'mid hip'),
    'right shoulder': ('right elbow',),
    'right elbow': ('right hand',),
    'right hand': (),
    'left shoulder': ('left elbow',),
    'left elbow': ('left hand',),
    'left hand': (),
    'mid hip': ('right hip', 'left hip'),
    'right hip': ('right knee',),
    'right knee': ('right ankle',),
    'right ankle': ('right heel', 'right big toe'),
    'left hip': ('left knee',),
    'left knee': ('left ankle',),
    'left ankle': ('left heel', 'left big toe'),
    'right eye': ('right ear', 'nose'),
    'left eye': ('left ear', 'nose'),
    'right ear': (),
    'left ear': (),
    'left big toe': ('left small toe',),
    'left small toe': (),
    'left heel': (),
    'right big toe': ('right small toe',),
    'right small toe': (),
    'right heel': ()
}

# threshold for if something is considered an error. Lower to make matching pose harder.
ERROR_THRESHOLD = 0.3

# threshold for what is a lot of error and what is a little error
HIGH_ERROR_BOUNDARY = 1
