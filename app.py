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


def distance_formula(coord1, coord2):
    return ((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2) ** 0.5


def get_file_number(file):
    end_index = file.index('_keypoints.json')
    return file[end_index-12: end_index]


def get_image_from_file_number(file_number, list_of_images):
    for f in list_of_images:
        if file_number in f:
            return f
    return None


extra_flag = ''

if USE_REAL_IMAGE == 1:
    image_files_path = os.path.abspath(IMAGE_FILE_DIR)
    list_of_images = glob.glob(image_files_path + '/*.png')
    for f in list_of_images:
        os.remove(f)
    extra_flag = ' --write_images ' + image_files_path

list_of_files = glob.glob(json_files_path + '/*.json')
for f in list_of_files:
    os.remove(f)

p = subprocess.Popen(OPENPOSE_BIN_FILE_DIR + 'openpose.bin --write_json ' + json_files_path + extra_flag +
            ' --display 0 --number_people_max 1 --render_pose 0 --net_resolution 320x320', shell=True, cwd=OPENPOSE_DIR)

print('Press c to capture. Press q to quit.')
time.sleep(7)
start = time.time()
k = -1
frame_body_selected = None
num_similar_frames = 0
last_file = None
last_frame_error = 0
while k != 113:
    list_of_files = glob.glob(json_files_path + '/*.json')
    curr_file = second_max_helper(list_of_files)

    if k == 99:
        frame_body_selected = Body(curr_file)

    if curr_file != last_file:
        flipped_already = False
        if USE_REAL_IMAGE:
            list_of_images = glob.glob(image_files_path + '/*.png')
            screen = cv2.imread(get_image_from_file_number(get_file_number(curr_file), list_of_images))
        else:
            screen = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
        curr_body = Body(curr_file)
        if curr_body.coord:
            part_locations = curr_body.coord
            for key in part_locations:
                if part_locations[key] and \
                        (key != 'right eye' and key != 'left eye' and key != 'right ear' and key != 'left ear'):
                    cv2.circle(screen, (int(part_locations[key][0]), int(part_locations[key][1])), PART_LOCATION_RADIUS,
                               COLOR_YELLOW, -1)
                    for connection in BODY_CONNECTIONS_DICT[key]:
                        if part_locations[connection]:
                            cv2.line(screen, (int(part_locations[key][0]), int(part_locations[key][1])),
                            (int(part_locations[connection][0]), int(part_locations[connection][1])), COLOR_YELLOW,
                            LINE_THICKNESS)
            if part_locations['nose'] and part_locations['neck'] and not USE_REAL_IMAGE:
                cv2.circle(screen, (int(part_locations['nose'][0]), int(part_locations['nose'][1])), int(HEAD_RATIO *
                distance_formula(part_locations['neck'], part_locations['nose'])), COLOR_YELLOW, LINE_THICKNESS)

            if frame_body_selected:
                if curr_body.coord_normalized and frame_body_selected.coord_normalized:
                    scale = curr_body.get_vert_scale_factor()
                    error_dict = subtract_dict_coord(curr_body, frame_body_selected, 'normalized')
                    circle_locations = get_scaled_dict_wrt_corner(frame_body_selected, scale, scale,
                        curr_body.get_part_coordinates('neck')[0], curr_body.get_part_coordinates('neck')[1])
                    error_exists = False
                    for key in circle_locations:
                        if curr_body.coord[key] and circle_locations[key]:
                            if get_part_error(error_dict, key) > ERROR_THRESHOLD:
                                cv2.circle(screen, circle_locations[key], CIRCLE_RADIUS, COLOR_RED, CIRCLE_THICKNESS)
                                error_exists = True
                            else:
                                cv2.circle(screen, circle_locations[key], CIRCLE_RADIUS, COLOR_GREEN, CIRCLE_THICKNESS)
                            if part_locations[key] and circle_locations[key]:
                                cv2.line(screen, (int(circle_locations[key][0]), int(circle_locations[key][1])),
                                (int(part_locations[key][0]), int(part_locations[key][1])), COLOR_RED,
                                ERROR_LINE_THICKNESS)
                            for connection in BODY_CONNECTIONS_DICT[key]:
                                if circle_locations[connection]:
                                    cv2.line(screen, (int(circle_locations[key][0]), int(circle_locations[key][1])),
                                             (int(circle_locations[connection][0]),
                                              int(circle_locations[connection][1])), COLOR_BLUE, LINE_THICKNESS)
                    flipped_screen = cv2.flip(screen, 1)
                    flipped_already = True
                    if last_frame_error-0.05 <= get_all_parts_average_error(curr_body, frame_body_selected,
                                                                            'normalized') <= last_frame_error + 0.05:
                        num_similar_frames += 1
                    else:
                        num_similar_frames = 0
                    if error_exists:
                        if num_similar_frames > 7:
                            text = get_max_error_part_comments(curr_body, frame_body_selected, 'normalized',
                                                               HIGH_ERROR_BOUNDARY)
                            text_placement_x = int(WIDTH/128)
                            text_placement_y = int(HEIGHT/72*5)
                            dy = 70
                            phrases = text.split('\n')
                            for line in phrases:
                                cv2.putText(flipped_screen, line, (text_placement_x, text_placement_y), 2, 1.5,
                                            COLOR_RED)
                                text_placement_y += dy

                        last_frame_error = get_all_parts_average_error(curr_body, frame_body_selected, 'normalized')
                    else:
                        cv2.putText(flipped_screen, 'Good Job!', (25, 695), 4, 4, COLOR_PURPLE)

                    graph_x_time.append(time.time()-start)
                    error = get_all_parts_average_error(curr_body,frame_body_selected, 'normalized')
                    cv2.putText(flipped_screen, 'Error: ' + str(round(error, 2)), (int(WIDTH/128*105),
                                                                                   int(HEIGHT/72*5)), 4, 1, COLOR_RED)
                    graph_y_error.append(error)
                cv2.imwrite(image_write_path + '/' + get_file_number(curr_file) + '.png', flipped_screen)

        if not flipped_already:
            flipped_screen = cv2.flip(screen, 1)
        winname = 'Test'
        cv2.namedWindow(winname)
        cv2.moveWindow(winname, 250, 250)
        cv2.imshow(winname, flipped_screen)
        last_file = curr_file
    k = cv2.waitKey(10)


subprocess.Popen('kill '+str(p.pid+1), shell=True)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.plot(graph_x_time, graph_y_error)
plt.show()

