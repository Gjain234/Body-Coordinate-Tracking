import json

body_parts = ['nose', 'neck', 'r_shoulder', 'r_elbow', 'r_wrist', 'l_shoulder', 'l_elbow', 'l_wrist', 'mid_hip',
              'r_hip', 'r_knee', 'r_ankle', 'l_hip', 'l_knee', 'l_ankle', 'r_eye', 'l_eye', 'r_ear', 'l_ear',
              'l_big_toe', 'l_small_toe', 'l_heel', 'r_big_toe', 'r_small_toe', 'r_heel']


def set_coordinates(body_dict, part, x, y):
    try:
        body_dict[part] = (round(x, 2), round(y, 2), body_dict[part][2])
    except (IndexError, KeyError):
        print('Incorrect dictionary type. Not all values present (set coord).')


def set_err(body_dict, part, error):
    try:
        body_dict[part] = (body_dict[part][0], body_dict[part][1], round(error, 2))
    except (IndexError, KeyError):
        print('Incorrect dictionary type. Not all values present (set err).')


def get_x(body_dict, part):
    try:
        return body_dict[part][0]
    except (IndexError, KeyError):
        print('Incorrect dictionary type. Not all values present (get x).')


def get_y(body_dict, part):
    try:
        return body_dict[part][1]
    except (IndexError, KeyError):
        print('Incorrect dictionary type. Not all values present (get y).')


def make_body_dict(json_file):
    try:
        body_coord = json_file['people'][0]['pose_keypoints_2d']
        body_dict = {}
        j = 0
        while j < len(body_parts):
            body_dict[(body_parts[j])] = (body_coord[3*j], body_coord[3*j+1], 0)
            j += 1
        return body_dict
    except (KeyError, IndexError):
        print('Incorrect file type. No body coordinates detected.')


def is_valid_part(body_dict, part):
    return not (get_x(body_dict, part) == 0 and get_y(body_dict, part) == 0)


def normalize(body_dict):
    origin_x = get_x(body_dict, 'neck')
    origin_y = get_y(body_dict, 'neck')
    for key in body_dict:
        if is_valid_part(body_dict, key):
            set_coordinates(body_dict, key, get_x(body_dict, key) - origin_x, -1 * get_y(body_dict, key) + origin_y)


def calc_error(body_dict_original, body_dict_test, part):
    if is_valid_part(body_dict_original, part) and is_valid_part(body_dict_test, part):
        x_error = get_x(body_dict_test, part) - get_x(body_dict_original, part)
        y_error = get_y(body_dict_test, part) - get_y(body_dict_original, part)
        total_error = (x_error ** 2 + y_error ** 2) ** 0.5
        return total_error
    else:
        set_coordinates(body_dict_test, part, 0, 0)
        return 0


def get_part_coord(dict, part):
    try:
        return dict[part]
    except KeyError:
        print('Incorrect file type. Not all body coordinates present.')


try:
    # open two files we want to compare. TODO: user gets to choose when want comparison.
    with open('/home/il/software/openpose/output_situp/000000000011_keypoints.json', 'r') as f:
        file_1 = json.load(f)

    with open('/home/il/software/openpose/output_situp/000000000010_keypoints.json', 'r') as f:
        file_2 = json.load(f)

except(FileNotFoundError, IndexError, KeyError):
    print('Incorrect JSON type. Cannot find expected values.')

original_body_dictionary = make_body_dict(file_1)
test_body_dictionary = make_body_dict(file_2)

normalize(original_body_dictionary)
normalize(test_body_dictionary)

for key in test_body_dictionary:
    set_err(test_body_dictionary, key, calc_error(original_body_dictionary, test_body_dictionary, key))

print(original_body_dictionary)
print(test_body_dictionary)
