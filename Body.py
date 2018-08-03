import json
body_parts = ['nose', 'neck', 'right shoulder', 'right elbow', 'right hand', 'left shoulder', 'left elbow',
              'left hand', 'mid hip', 'right hip', 'right knee', 'right ankle', 'left hip', 'left knee', 'left ankle',
              'right eye', 'left eye', 'right ear', 'left ear', 'left big toe', 'left small toe', 'left heel',
              'right big toe', 'right small toe', 'right heel']


#todo: helper function for inside if statements
def subtract_dict_coord(body1, body2, wrt='relative'):
    try:
        new_dict = {}
        if wrt == 'relative':
            for key in body1.coord_wrt_neck:
                if body1.coord_wrt_neck[key] is None or body2.coord_wrt_neck[key] is None:
                    new_dict[key] = None
                else:
                    new_dict[key] = (body1.coord_wrt_neck[key][0] - body2.coord_wrt_neck[key][0],
                                     body1.coord_wrt_neck[key][1] - body2.coord_wrt_neck[key][1])
            return new_dict
        if wrt == 'absolute':
            for key in body1.coord:
                if body1.coord[key] is None or body2.coord[key] is None:
                    new_dict[key] = None
                else:
                    new_dict[key] = (body1.coord[key][0] - body2.coord[key][0], body1.coord[key][1] -
                                     body2.coord[key][1])
            return new_dict
        if wrt == 'normalized':
            for key in body1.coord_normalized:
                if body1.coord_normalized[key] is None or body2.coord_normalized[key] is None:
                    new_dict[key] = None
                else:
                    new_dict[key] = (body1.coord_normalized[key][0] - body2.coord_normalized[key][0],
                                     body1.coord_normalized[key][1] - body2.coord_normalized[key][1])
            return new_dict
        print('invalid measurement type. Choose "relative", "normalized", or "absolute"')
        return None
    except(KeyError, IndexError, AttributeError):
        print('Either body1 or body2 or both are not valid body objects')


#todo: make y default None
def get_scaled_dict(body, scale_x, scale_y):
    new_dict = {}
    try:
        for part in body.coord_normalized:
            if not new_dict[part]:
                new_dict[part] = (body.coord_normalized[part][0] * scale_x, body.coord_normalized[part][1] * scale_y)
    except(IndexError, AttributeError, KeyError):
        print('Invalid dictionary type cannot be scaled')
    return new_dict


def get_part_error(error_dict, part):
    try:
        if error_dict[part]:
            return round((error_dict[part][0] ** 2 + error_dict[part][1] ** 2) ** 0.5, 3)
        else:
            return None
    except(KeyError, IndexError, TypeError):
        print('Invalid Dictionary type when finding error')


def get_all_parts_average_error(body1, body2, measurement):
    error_dict = subtract_dict_coord(body1, body2, measurement)
    total_error = 0
    num_parts = 0
    for key in error_dict:
        if error_dict[key]:
            num_parts += 1
            total_error += get_part_error(error_dict, key)
    return total_error/num_parts


def get_a_little_or_a_lot(threshold, value):
    if value < threshold:
        return 'a little '
    if value > threshold:
        return 'a lot '


def get_part_comments(error_dict, part, threshold_for_a_lot, error=0):
    try:
        horizontal_comments = False
        if error_dict[part]:
            final_message = ''
            if abs(error_dict[part][0]) > error:
                horizontal_comments = True
                if error_dict[part][0] < 0:
                    final_message += 'move ' + part + ' right '
                else:
                    final_message += 'move ' + part + ' left '
                final_message += get_a_little_or_a_lot(threshold_for_a_lot, abs(error_dict[part][0]))
            if abs(error_dict[part][1]) > error:
                if not horizontal_comments:
                    if error_dict[part][1] < 0:
                        final_message += 'move ' + part + ' up '
                    else:
                        final_message += 'move ' + part + ' down '
                else:
                    if error_dict[part][1] < 0:
                        final_message += '\nand up '
                    else:
                        final_message += '\nand down '
                final_message += get_a_little_or_a_lot(threshold_for_a_lot, abs(error_dict[part][1]))
            return final_message
        else:
            return None
    except(KeyError, IndexError, TypeError):
        print('Invalid Dictionary type when getting part comments')


def get_max_error_part_comments(body1, body2, measurement, threshold_for_a_lot):
    error_dict = subtract_dict_coord(body1, body2, measurement)
    max_err = 0
    max_key = ''
    for key in error_dict:
        if get_part_error(error_dict, key) > max_err:
            max_err = get_part_error(error_dict, key)
            max_key = key
    return get_part_comments(error_dict, max_key, threshold_for_a_lot)


def get_full_body_comments(body1, body2, ball_error, measurement, threshold_for_a_lot):
    error_dict = subtract_dict_coord(body1, body2, measurement)
    ball_xy_component = ball_error / (2 ** 0.5)
    all_comments = ''
    for key in error_dict:
        if error_dict[key]:
            if get_part_error(error_dict, key) > ball_error:
                all_comments += get_part_comments(error_dict, key, threshold_for_a_lot, ball_xy_component) + ' '
    return all_comments


def normalize_1d(body, orientation):
    if orientation == 'horizontal':
        unit = ((body.coord_wrt_neck['right_shoulder'][0] - body.coord_wrt_neck['left_shoulder'][0]) ** 2 +
                (body.coord_wrt_neck['right_shoulder'][1] - body.coord_wrt_neck['left_shoulder'][1]) ** 2) ** 0.5 / 2
    elif orientation == 'vertical':
        unit = body.coord_wrt_neck['nose'][1] - body.coord_wrt_neck['neck'][1]
    else:
        print('please specify orientation argument as "vertical" or "horizontal"')
        return None
    new_dict = {}
    for key in body.coord_wrt_neck:
        if body.coord_wrt_neck[key]:
            new_dict[key] = (body.coord_wrt_neck[key][0] / unit, body.coord_wrt_neck[key][1] / unit)
        else:
            new_dict[key] = None
    return new_dict


def normalize_2d(self):
    unit_x = ((self.coord_wrt_neck['right_shoulder'][0] - self.coord_wrt_neck['left_shoulder'][0]) ** 2 +
              (self.coord_wrt_neck['right_shoulder'][1] - self.coord_wrt_neck['left_shoulder'][1]) ** 2) ** 0.5 / 2
    unit_y = self.coord_wrt_neck['nose'][1] - self.coord_wrt_neck['neck'][1]
    new_dict = {}
    for key in self.coord_wrt_neck:
        if self.coord_wrt_neck[key]:
            new_dict[key] = (self.coord_wrt_neck[key][0] / unit_x, self.coord_wrt_neck[key][1] / unit_y)
        else:
            new_dict[key] = None
    return new_dict


class Body:

    def __init__(self, file_name, wrt_part='neck', normalize_type='y'):
        try:
            with open(file_name) as f:
                json_file = json.load(f)
            body_coord = json_file['people'][0]['pose_keypoints_2d']
            self.coord = {}
            j = 0
            while j < len(body_parts):
                if not(body_coord[3 * j] == 0 and body_coord[3 * j + 1] == 0):
                    self.coord[(body_parts[j])] = (body_coord[3 * j], body_coord[3 * j + 1])
                else:
                    self.coord[(body_parts[j])] = None
                j += 1

            self.coord_wrt_neck = {}
            origin = self.coord[wrt_part]

            for key in self.coord:
                if self.coord[key]:
                    curr_coord = self.get_part_coordinates(key)
                    self.coord_wrt_neck[key] = (round(-1 * curr_coord[0] + origin[0], 3), round(-1 * curr_coord[1] +
                                                                                                origin[1], 3))
                else:
                    self.coord_wrt_neck[key] = None
            if normalize_type == 'xy':
                self.coord_normalized = {}
                unit_x = ((self.coord_wrt_neck['right_shoulder'][0] - self.coord_wrt_neck['left_shoulder'][0]) ** 2 +
                          (self.coord_wrt_neck['right_shoulder'][1] - self.coord_wrt_neck['left_shoulder'][
                              1]) ** 2) ** 0.5 / 2
                unit_y = self.coord_wrt_neck['nose'][1] - self.coord_wrt_neck['neck'][1]
                self.coord_normalized = {}
                for key in self.coord_wrt_neck:
                    if self.coord_wrt_neck[key]:
                        self.coord_normalized[key] = (self.coord_wrt_neck[key][0] / unit_x, self.coord_wrt_neck[key][1] / unit_y)
                    else:
                        self.coord_normalized[key] = None
            else:
                if normalize_type == 'x':
                    unit = ((self.coord_wrt_neck['right_shoulder'][0] - self.coord_wrt_neck['left_shoulder'][0]) ** 2 +
                            (self.coord_wrt_neck['right_shoulder'][1] - self.coord_wrt_neck['left_shoulder'][
                                1]) ** 2) ** 0.5 / 2
                elif normalize_type == 'y':
                    unit = self.coord_wrt_neck['nose'][1] - self.coord_wrt_neck['neck'][1]
                else:
                    print('please enter valid normalizing type: x, y, or xy. Normalized coord NOT set correctly.')
                self.coord_normalized = {}
                for key in self.coord_wrt_neck:
                    if self.coord_wrt_neck[key]:
                        self.coord_normalized[key] = (self.coord_wrt_neck[key][0] / unit, self.coord_wrt_neck[key][1] / unit)
                    else:
                        self.coord_normalized[key] = None
        except (IndexError, KeyError):
            self.coord = None
            self.coord_wrt_neck = None
            self.coord_normalized = None
        except TypeError:
            self.coord_normalized = None
            self.coord_wrt_neck = None

    def get_dict(self):
        return self.coord

    def get_part_coordinates(self, part):
        return self.coord[part]

    def set_dict_wrt_neck(self):
        origin = self.get_part_coordinates('neck')
        new_dict = {}
        for key in self.coord:
            if self.coord[key]:
                curr_coord = self.get_part_coordinates(key)
                new_dict[key] = (round(-1 * curr_coord[0] + origin[0], 3), round(-1 * curr_coord[1] + origin[1], 3))
            else:
                new_dict[key] = None

        return new_dict

    def get_vert_scale_factor(self):
        return self.coord_wrt_neck['nose'][1] - self.coord_wrt_neck['neck'][1]


