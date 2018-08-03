import subprocess
import time
import cv2
import glob
import os
from Constants import *
from Body import *
import numpy as np
import matplotlib.pyplot as plt


json_files_path = os.path.abspath(JSON_FILE_DIR)
image_write_path = os.path.abspath(IMAGE_WRITE_DIR)
graph_x_time = []
graph_y_error = []


def second_max_helper(file_list):
    """ Return the second most recently modified from a list of files.
        Compensates for not reading files as they are written
    """
    max_time = 0
    sec_max_time = 0
    try:
        max_file = file_list[0]
    except IndexError:
        print(None)
    sec_max_file = None
    for file in file_list:
        file_time = os.path.getctime(file)
        if file_time > max_time:
            sec_max_time = max_time
            sec_max_file = max_file
            max_time = file_time
            max_file = file
        elif sec_max_time < file_time < max_time:
            sec_max_time = file_time
            sec_max_file = file
    return sec_max_file


def get_file_number(file):
    end_index = file.index('_keypoints.json')
    return file[end_index-12: end_index]


def get_image_from_file_number(file_number, list_of_images):
    """ Return corresponding image file to json file.
        Only used when want real images displayed
    """
    for f in list_of_images:
        if file_number in f:
            return f
    return None


def distance_formula(coord1, coord2):
    return ((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2) ** 0.5


def _draw_connections_from_limb(coordinate_dictionary, part, color):
    """ Draw all connecting limbs from a body part """
    for joint in BODY_CONNECTIONS_DICT[part]:
        if coordinate_dictionary[joint]:
            cv2.line(screen, (int(coordinate_dictionary[part][0]), int(coordinate_dictionary[part][1])),
                     (int(coordinate_dictionary[joint][0]), int(coordinate_dictionary[joint][1])),
                     color, LINE_THICKNESS)


def draw_curr_body_frame(body):
    """ Draw user's current pose
        Only used for stick figure version
    """
    coordinate_dictionary = body.coord
    for part in coordinate_dictionary:
        if coordinate_dictionary[part] and \
                (part != 'right eye' and part != 'left eye' and part != 'right ear' and part != 'left ear'):
            cv2.circle(screen, (int(coordinate_dictionary[part][0]), int(coordinate_dictionary[part][1])),
                       PART_LOCATION_RADIUS, COLOR_YELLOW, -1)
            _draw_connections_from_limb(coordinate_dictionary, part, COLOR_YELLOW)


def draw_head(body):
    if body.coord['nose'] and body.coord['neck']:  # draw head
        cv2.circle(screen, (int(body.coord['nose'][0]), int(body.coord['nose'][1])), int(HEAD_RATIO *
        distance_formula(body.coord['neck'], body.coord['nose'])), COLOR_YELLOW, LINE_THICKNESS)


def draw_error_body_frame(body_selected, body_real_time):
    """ Draw goal pose and error-related annotations on body """
    body_error_exists = False
    scale = body_real_time.get_vert_scale_factor()
    error_dict = subtract_dict_coord(body_real_time, body_selected, 'normalized')
    circle_locations = get_scaled_part_locations_wrt_corner(body_selected, scale, scale,
        body_real_time.get_part_coordinates('neck')[0], body_real_time.get_part_coordinates('neck')[1])
    for part in error_dict:
        if error_dict[part] and circle_locations[part]:
            if get_part_error(error_dict, part) > ERROR_THRESHOLD:
                cv2.circle(screen, circle_locations[part], CIRCLE_RADIUS, COLOR_RED, CIRCLE_THICKNESS)
                body_error_exists = True
            else:
                cv2.circle(screen, circle_locations[part], CIRCLE_RADIUS, COLOR_GREEN, CIRCLE_THICKNESS)

            cv2.line(screen, (int(circle_locations[part][0]), int(circle_locations[part][1])),
                     (int(body_real_time.coord[part][0]), int(body_real_time.coord[part][1])), COLOR_RED,
                     ERROR_LINE_THICKNESS)
            _draw_connections_from_limb(circle_locations, part, COLOR_BLUE)
    return body_error_exists


def get_scaled_part_locations_wrt_corner(body, scale_x, scale_y, origin_x, origin_y):
    """ Return a dictionary of pixel coordinates for a scaled version of desired pose.
        Also convert coordinates to be with respect to top left for pixel drawing
    """
    new_dict = {}
    try:
        for part in body.coord_normalized:
            if body.coord_normalized[part] and \
                    (part != 'right eye' and part != 'left eye' and part != 'right ear' and part != 'left ear'):
                new_dict[part] = (int(origin_x - body.coord_normalized[part][0] * scale_x), int(origin_y -
                                  body.coord_normalized[part][1] * scale_y))
            else:
                new_dict[part] = None
    except(IndexError, AttributeError, KeyError):
        print('Invalid dictionary type cannot be scaled wrt origin')
    return new_dict


def write_instructions(body_real_time, body_selected):
    """ Write instructions on top left corner of screen.
        Should only be called if user has been still for some time.
    """
    text = get_max_error_part_comments(body_real_time, body_selected, 'normalized', HIGH_ERROR_BOUNDARY)
    text_placement_x = int(WIDTH / 128)
    text_placement_y = int(HEIGHT / 72 * 5)
    dy = 70
    phrases = text.split('\n')
    for line in phrases:
        cv2.putText(screen, line, (text_placement_x, text_placement_y), 2, 1.5,
                    COLOR_RED)
        text_placement_y += dy


def graph_data(current_time, curr_error):
    graph_x_time.append(current_time - start)
    graph_y_error.append(curr_error)


def display_error(curr_error):
    """ Give total error count in top right corner """
    cv2.putText(screen, 'Error: ' + str(round(curr_error, 2)), (int(WIDTH / 128 * 105),
                                                                int(HEIGHT / 72 * 5)), 4, 1, COLOR_RED)


def show_screen(curr_screen):
    winname = 'Test'
    cv2.namedWindow(winname)
    cv2.moveWindow(winname, 250, 250)
    cv2.imshow(winname, curr_screen)


extra_flag = ''  # flag for openpose command if we want to use real images

if USE_REAL_IMAGE:
    image_files_path = os.path.abspath(IMAGE_FILE_DIR)
    list_of_images = glob.glob(image_files_path + '/*.png')
    for f in list_of_images:
        os.remove(f)
    extra_flag = ' --write_images ' + image_files_path

list_of_files = glob.glob(json_files_path + '/*.json')
for f in list_of_files:
    os.remove(f)

# command to run openpose in the background. Look at openpose demo github page to read about specific flags
p = subprocess.Popen(OPENPOSE_BIN_FILE_DIR + 'openpose.bin --write_json ' + json_files_path + extra_flag +
            ' --display 0 --number_people_max 1 --render_pose 0 --net_resolution 320x320', shell=True, cwd=OPENPOSE_DIR)

print('Press c to capture. Press q to quit.')
time.sleep(5)  # gives openpose time to start up
start = time.time() # to generate error vs time graph
k = -1  # will be used for keypress
frame_body_selected = None
last_file = None
num_similar_frames = 0
last_frame_error = 0

while k != 113:  # before user presses 'q'
    list_of_files = glob.glob(json_files_path + '/*.json')
    curr_file = second_max_helper(list_of_files)
    body_flipped = False  # for screen flipping logic later
    if k == 99:  # if user presses 'c'
        frame_body_selected = Body(curr_file)

    if curr_file != last_file:  # if there is an update to what should be displayed on screen
        if USE_REAL_IMAGE:
            list_of_images = glob.glob(image_files_path + '/*.png')
            screen = cv2.imread(get_image_from_file_number(get_file_number(curr_file), list_of_images))
        else:
            screen = np.zeros((HEIGHT, WIDTH, 3), np.uint8)  # black screen
        curr_body = Body(curr_file)
        if curr_body.coord:  # If there is someone on the screen
            draw_curr_body_frame(curr_body)

            if not USE_REAL_IMAGE:
                draw_head(curr_body)

            if frame_body_selected:  # if capture has been detected
                if curr_body.coord_normalized and frame_body_selected.coord_normalized:
                    # if nose and neck are in captured frame and normalization is possible

                    error_exists = draw_error_body_frame(frame_body_selected, curr_body)
                    if CAMERA_FLIP:
                        screen = cv2.flip(screen, 1)
                        body_flipped = True

                    curr_average_error = get_all_parts_average_error(curr_body, frame_body_selected, 'normalized')
                    if last_frame_error-0.05 <= curr_average_error <= last_frame_error + 0.05:
                        num_similar_frames += 1
                    else:
                        num_similar_frames = 0
                    if error_exists:
                        if num_similar_frames > 7:
                            write_instructions(curr_body, frame_body_selected)

                        last_frame_error = curr_average_error
                    else:
                        cv2.putText(screen, 'Good Job!', (25, 695), 4, 4, COLOR_PURPLE)

                    graph_data(time.time(), curr_average_error)
                    display_error(curr_average_error)

                if SAVE_IMAGES_WITH_ANNOTATION:
                    cv2.imwrite(image_write_path + '/' + get_file_number(curr_file) + '.png', screen)

        if CAMERA_FLIP and not body_flipped:
            screen = cv2.flip(screen, 1)

        show_screen(screen)
    last_file = curr_file
    k = cv2.waitKey(10)  # update in the case of a keypress


subprocess.Popen('kill '+str(p.pid+1), shell=True)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.plot(graph_x_time, graph_y_error)
plt.show()

