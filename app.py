import subprocess
import time
import cv2
import glob
import os
from Body import *

IMAGE_DIR = '/home/il/software/openpose/gauritest'
JSON_FILE_DIR = '/home/il/software/openpose/gauritestjson'

IMAGE_WRITE_DIR = './images/'

NUM_X_PIXELS = 1280
NUM_Y_PIXELS = 720

COLOR_RED = (0, 0, 255) # Red Green Blue
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)


def sec_max_helper(file_list):
    max_time = 0
    sec_max_time = 0
    try:
        max_file = file_list[0]
    except IndexError:
        print('no files in current directory')
    sec_max_file = ''
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
    end_index = file.index('_rendered.png')
    return file[end_index-12: end_index]


list_of_images = glob.glob(IMAGE_DIR + '/*.png')
list_of_files = glob.glob(JSON_FILE_DIR + '/*.json')
for f in list_of_files:
    os.remove(f)
for f in list_of_images:
    os.remove(f)


p = subprocess.Popen('./build/examples/openpose/openpose.bin --write_json ' + JSON_FILE_DIR +
                     ' --write_images ' + IMAGE_DIR + ' --display 0 --number_people_max 1', shell=True,
                     cwd='/home/il/software/openpose')

k = -1
frame_body_selected = None

print('Press c to capture. Press q to quit.')
time.sleep(5)
while k != 113:
    list_of_images = glob.glob(IMAGE_DIR + '/*.png')
    list_of_files = glob.glob(JSON_FILE_DIR + '/*.json')
    curr_image = sec_max_helper(list_of_images)
    img = cv2.imread(curr_image)

    if frame_body_selected:
        curr_body = Body(sec_max_helper(list_of_files))
        if curr_body.coord_normalized:
            scale = curr_body.get_vert_scale_factor()
            error_dict = subtract_dict_coord(curr_body, frame_body_selected, 'normalized')
            circle_locations = get_scaled_dict_wrt_corner(frame_body_selected, scale, scale,
                curr_body.get_part_coordinates('neck')[0], curr_body.get_part_coordinates('neck')[1])
            error_threshold = 0.3
            error_exists = False
            for key in circle_locations:
                if curr_body.coord[key]:
                    circle_thickness = 1
                    circle_radius = 15
                    if get_part_error(error_dict, key) > error_threshold:
                        cv2.circle(img, circle_locations[key], circle_radius, COLOR_RED, circle_thickness)
                        error_exists = True
                    else:
                        cv2.circle(img, circle_locations[key], circle_radius, COLOR_GREEN, circle_thickness)
            if error_exists:
                cv2.putText(img, get_full_body_comments(curr_body, frame_body_selected, error_threshold, 'normalized'),
                            (25, 695), 2, 0.4, (255, 0, 255))
            else:
                cv2.putText(img, 'Good Job!', (25, 695), 4, 4, (255, 0, 255))

    if k == 99:
        latest_file = sec_max_helper(list_of_files)
        print(latest_file)
        frame_body_selected = Body(latest_file)

    cv2.imwrite(IMAGE_WRITE_DIR + get_file_number(curr_image) + '.png', img)
    cv2.imshow('img', img)
    k = cv2.waitKey(10)

subprocess.Popen('kill '+str(p.pid+1), shell=True)

