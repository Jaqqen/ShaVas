import random, math, cv2
import numpy as np
import copy
from collections import Counter
from frame_drawing import getCornerDistancesDictionary, getCornersOfDrawingFrame, getMaxMinCornerValues, getShapeInfo

TOP = 'TOP'
RIGHT = 'RIGHT'
LEFT = 'LEFT'
BOTTOM = 'BOTTOM'

VERTICAL = 'VERTICAL'
HORIZONTAL = 'HORIZONTAL'

TRANSLATION = {TOP: TOP,
               RIGHT: RIGHT,
               BOTTOM: BOTTOM,
               LEFT: LEFT}

AXIS_OPTIONS = [VERTICAL, HORIZONTAL]
VERTICAL_OPTIONS = [TRANSLATION[TOP], TRANSLATION[BOTTOM]]
HORIZONTAL_OPTIONS = [TRANSLATION[LEFT], TRANSLATION[RIGHT]]

ROTATION = {TOP: TOP,
            RIGHT: RIGHT,
            BOTTOM: BOTTOM,
            LEFT: LEFT}

TOP_LEFT = 'TOP_LEFT'
TOP_RIGHT = 'TOP_RIGHT'
BOTTOM_LEFT = 'BOTTOM_LEFT'
BOTTOM_RIGHT = 'BOTTOM_RIGHT'
X = 'X'
Y = 'Y'

EQUAL = 'EQUAL'
UNEQUAL = 'UNEQUAL'


P_TRANSFORMATION = {TOP: TOP,
                    RIGHT: RIGHT,
                    BOTTOM: BOTTOM,
                    LEFT: LEFT,
                    TOP_LEFT: TOP_LEFT,
                    TOP_RIGHT: TOP_RIGHT,
                    BOTTOM_LEFT: BOTTOM_LEFT,
                    BOTTOM_RIGHT: BOTTOM_RIGHT,
                    EQUAL: EQUAL,
                    UNEQUAL: UNEQUAL
                   }

ALL_POSSIBLE_DRAGABLE_CORNERS = [P_TRANSFORMATION[TOP_LEFT],
                                 P_TRANSFORMATION[TOP_RIGHT],
                                 P_TRANSFORMATION[BOTTOM_LEFT],
                                 P_TRANSFORMATION[BOTTOM_RIGHT]]

NO_ROTATION_PARAM = 0
NO_SCALE_PARAM = 1

def getRandomNegativeDistance(endValue):
    return random.randint(1, endValue - 1) * (-1) if (endValue > 2) else 0

def getRandomPositiveDistance(endValue):
    return random.randint(1, endValue - 1) if (endValue > 2) else 0

def equalOrUnequal():
    global EQUAL, UNEQUAL
    return random.choice([P_TRANSFORMATION[EQUAL], P_TRANSFORMATION[UNEQUAL]])

def getRandomStretchCompress():
    return random.randint(1, 3) if (random.randint(0, 1) == 0) else random.randint(1, 3) * -1

def getRandomExtraVerticalTranslation(_vertical_translation, distances_dict):
    global TRANSLATION, TOP, BOTTOM

    extra_vertical_translation = random.choice([_vertical_translation, None])
    if (extra_vertical_translation == None):
        return 0
    elif (extra_vertical_translation == TRANSLATION[TOP]):
        return getRandomNegativeDistance(distances_dict[TRANSLATION[TOP]])
    else:
        return getRandomPositiveDistance(distances_dict[TRANSLATION[BOTTOM]])
    
def getRandomExtraHorizontalTranslation(_horizontal_translation, distances_dict):
    global TRANSLATION, LEFT, RIGHT

    extra_horizontal_translation = random.choice([_horizontal_translation, None])
    if (extra_horizontal_translation == None):
        return 0
    elif (extra_horizontal_translation == TRANSLATION[LEFT]):
        return getRandomNegativeDistance(distances_dict[TRANSLATION[LEFT]])
    else:
        return getRandomPositiveDistance(distances_dict[TRANSLATION[RIGHT]])

def getMaxRotationAngleOfSide(side_corner_angle, distance_to_side, new_AK):
    side_rest_angle = 90 - side_corner_angle
    new_GK = distance_to_side/math.sin(math.radians(side_rest_angle))

    max_angle = math.degrees(math.atan(new_GK/new_AK))   

    return 180 if (max_angle >= 45) else max_angles

#####################
#### TRANSLATION ####
#####################
def getTranslationOfImage(image_array):
    global TRANSLATION, AXIS_OPTIONS, VERTICAL_OPTIONS, HORIZONTAL_OPTIONS
    global TOP, RIGHT, BOTTOM, LEFT
    # print('==> TRANSLATION <==')
    cols, rows = getShapeInfo(image_array)
    
    current_distances_dict = getCornerDistancesDictionary(getMaxMinCornerValues(image_array), image_array)
    
    y_value = 0
    x_value = 0
    
    vertical_or_horizontal = random.choice(AXIS_OPTIONS)
    random_vertical_translation = random.choice(VERTICAL_OPTIONS)
    random_horizontal_translation = random.choice(HORIZONTAL_OPTIONS)
    
    if (vertical_or_horizontal == VERTICAL):
        if (random_vertical_translation == TRANSLATION[TOP]):
            y_value = getRandomNegativeDistance(current_distances_dict[TRANSLATION[TOP]])
        else:
            y_value = getRandomPositiveDistance(current_distances_dict[TRANSLATION[BOTTOM]])
        x_value = getRandomExtraHorizontalTranslation(random_horizontal_translation, current_distances_dict)
    else:
        if (random_horizontal_translation == TRANSLATION[LEFT]):
            x_value = getRandomNegativeDistance(current_distances_dict[TRANSLATION[LEFT]])
        else:
            x_value = getRandomPositiveDistance(current_distances_dict[TRANSLATION[RIGHT]])
        y_value = getRandomExtraVerticalTranslation(random_vertical_translation, current_distances_dict)

    M_transformation = np.float32([[1, 0, x_value], [0, 1, y_value]])
    dst_transformation = cv2.warpAffine(image_array, M_transformation, (cols, rows), borderValue=255)
    
    return dst_transformation

###############
#### SCALE ####
###############
def getScaleOfImage(image_array):
    global NO_ROTATION_PARAM, TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, X, Y
    # print('==> SCALE <==')
    cols, rows = getShapeInfo(image_array)

    scale = round(random.uniform(0.65, 0.95), 2)
    corners = getCornersOfDrawingFrame(getMaxMinCornerValues(image_array))

    div_x = round(random.uniform(1.75, 2.25), 3)
    div_y = round(random.uniform(1.75, 2.25), 3)

    x_center = corners[TOP_LEFT][X] + math.floor(
        (corners[TOP_RIGHT][X] - corners[TOP_LEFT][X]) / div_x)

    y_center = corners[TOP_LEFT][Y] + math.floor(
        (corners[BOTTOM_LEFT][Y] - corners[TOP_LEFT][Y]) / div_y)

    M_transformation = cv2.getRotationMatrix2D((x_center, y_center), NO_ROTATION_PARAM, 0.5)
    dst_transformation = cv2.warpAffine(image_array, M_transformation, (cols, rows), borderValue=255)
    
    return dst_transformation

##################
#### ROTATION ####
##################
def getRotationOfImage(image_array):
    global ROTATION, NO_SCALE_PARAM, TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT, X, Y
    global TOP, RIGHT, BOTTOM, LEFT
    # print('==> ROTATION <==')
    cols, rows = getShapeInfo(image_array)
    
    current_distances_dict = getCornerDistancesDictionary(getMaxMinCornerValues(image_array), image_array)
    corners = getCornersOfDrawingFrame(getMaxMinCornerValues(image_array))
    
    X_half_drawing = (corners[TOP_RIGHT][X] - corners[TOP_LEFT][X]) / 2
    Y_half_drawing = (corners[BOTTOM_RIGHT][Y] - corners[TOP_RIGHT][Y]) / 2
    hypot_drawing_forth = math.hypot(X_half_drawing, Y_half_drawing)
    
    top_bottom_corner_angle = math.degrees(math.sin(Y_half_drawing/hypot_drawing_forth))
    left_right_corner_angle = math.degrees(math.sin(X_half_drawing/hypot_drawing_forth))
    
    #side_corner_angle, distance_to_side, new_AK
    top_max_angle = getMaxRotationAngleOfSide(top_bottom_corner_angle, current_distances_dict[ROTATION[TOP]], hypot_drawing_forth)
    right_max_angle = getMaxRotationAngleOfSide(left_right_corner_angle, current_distances_dict[ROTATION[RIGHT]], hypot_drawing_forth)
    bottom_max_angle = getMaxRotationAngleOfSide(top_bottom_corner_angle, current_distances_dict[ROTATION[BOTTOM]], hypot_drawing_forth)
    left_max_angle = getMaxRotationAngleOfSide(left_right_corner_angle, current_distances_dict[ROTATION[LEFT]], hypot_drawing_forth)
    
    
    max_rot_angle = round(min([top_max_angle, right_max_angle, bottom_max_angle, left_max_angle]), 2)
    rotation = random.uniform(-max_rot_angle, max_rot_angle)
    
    x_center = corners[TOP_LEFT][X] + math.floor(X_half_drawing)
    y_center = corners[TOP_LEFT][Y] + math.floor(Y_half_drawing)
    
    M_transformation = cv2.getRotationMatrix2D((x_center, y_center), rotation, NO_SCALE_PARAM)
    dst_transformation = cv2.warpAffine(image_array, M_transformation, (cols, rows), borderValue=255)

    return dst_transformation

####################################
#### PERSPECTIVE TRANSFORMATION ####
####################################
def getPerspectiveTransformationOfImage(image_array):  
    global ALL_POSSIBLE_DRAGABLE_CORNERS, P_TRANSFORMATION, LEFT, RIGHT, TOP, BOTTOM, EQUAL
    global TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT, X, Y
    # print('===> PERSPECTIVE TRANSFORMATION <===')
    cols, rows = getShapeInfo(image_array)

    corners_of_original = getCornersOfDrawingFrame(getMaxMinCornerValues(image_array))
    start_top_left = corners_of_original[P_TRANSFORMATION[TOP_LEFT]]
    start_top_right = corners_of_original[P_TRANSFORMATION[TOP_RIGHT]]
    start_bottom_left = corners_of_original[P_TRANSFORMATION[BOTTOM_LEFT]]
    start_bottom_right = corners_of_original[P_TRANSFORMATION[BOTTOM_RIGHT]]
    
    corners_of_dst = copy.deepcopy(corners_of_original)
    dst_top_left = corners_of_dst[P_TRANSFORMATION[TOP_LEFT]]
    dst_top_right = corners_of_dst[P_TRANSFORMATION[TOP_RIGHT]]
    dst_bottom_left = corners_of_dst[P_TRANSFORMATION[BOTTOM_LEFT]]
    dst_bottom_right = corners_of_dst[P_TRANSFORMATION[BOTTOM_RIGHT]]
    
    current_distances_dict = getCornerDistancesDictionary(getMaxMinCornerValues(image_array), image_array)
    
    # get random amount of corners to drag, results = 1 - 4
    random_amount_of_corners_to_drag = random.randint(1, len(ALL_POSSIBLE_DRAGABLE_CORNERS))
    
    # create a random list of corner drag operations
    corners_to_drag = []
    added_drag_corner_indices = []
    
    for index in range(random_amount_of_corners_to_drag):
        random_drag_corner_index = random.randint(0, len(ALL_POSSIBLE_DRAGABLE_CORNERS) - 1)
        
        while True:
            if (random_drag_corner_index not in added_drag_corner_indices):
                # add random corner index to the list to check for
                added_drag_corner_indices.append(random_drag_corner_index)
                # append the corner with the specific index
                corners_to_drag.append(ALL_POSSIBLE_DRAGABLE_CORNERS[random_drag_corner_index])
            else:
                random_drag_corner_index = random.randint(0, len(ALL_POSSIBLE_DRAGABLE_CORNERS) - 1)
                continue
            break    
    
    # counts the occurences of the words 'top', 'left', 'right', 'bottom'
    amount_of_corner_occurences = []
    
    for corner in corners_to_drag:
         amount_of_corner_occurences = amount_of_corner_occurences + corner.split('_')

    # this contains all occurences in dict by the keys 'top', 'left', 'right', 'bottom'
    counts_of_corner_occurences = Counter(amount_of_corner_occurences)    
    
    # ==// TOP \\==
    if (counts_of_corner_occurences[P_TRANSFORMATION[TOP]] == 2):
        if (equalOrUnequal() == P_TRANSFORMATION[EQUAL]):
            equal_stretch_compress = getRandomStretchCompress()
            dst_top_left[Y] = dst_top_left[Y] + equal_stretch_compress
            dst_top_right[Y] = dst_top_right[Y] + equal_stretch_compress
        else:
            dst_top_left[Y] = dst_top_left[Y] + getRandomStretchCompress()
            dst_top_right[Y] = dst_top_right[Y] + getRandomStretchCompress()
        del counts_of_corner_occurences[P_TRANSFORMATION[TOP]]
        
    elif (counts_of_corner_occurences[P_TRANSFORMATION[TOP]] == 1):
        if (P_TRANSFORMATION[TOP_LEFT] in corners_to_drag):
            dst_top_left[Y] = dst_top_left[Y] + getRandomStretchCompress()
        else:
            dst_top_right[Y] = dst_top_right[Y] + getRandomStretchCompress()
        del counts_of_corner_occurences[P_TRANSFORMATION[TOP]]
        
    # ==// LEFT \\==
    if (counts_of_corner_occurences[P_TRANSFORMATION[LEFT]] == 2):
        if (equalOrUnequal() == P_TRANSFORMATION[EQUAL]):
            equal_stretch_compress = getRandomStretchCompress()
            dst_top_left[X] = dst_top_left[X] + equal_stretch_compress
            dst_bottom_left[X] = dst_bottom_left[X] + equal_stretch_compress
        else:
            dst_top_left[X] = dst_top_left[X] + getRandomStretchCompress()
            dst_bottom_left[X] = dst_bottom_left[X] + getRandomStretchCompress()
        del counts_of_corner_occurences[P_TRANSFORMATION[LEFT]]
        
    elif (counts_of_corner_occurences[P_TRANSFORMATION[LEFT]] == 1):        
        if (P_TRANSFORMATION[TOP_LEFT] in corners_to_drag):
            dst_top_left[X] = dst_top_left[X] + getRandomStretchCompress()
        else:
            dst_bottom_left[X] = dst_bottom_left[X] + getRandomStretchCompress()
        del counts_of_corner_occurences[P_TRANSFORMATION[LEFT]]
        
    # ==// RIGHT \\==
    if (counts_of_corner_occurences[P_TRANSFORMATION[RIGHT]] == 2):
        if (equalOrUnequal() == P_TRANSFORMATION[EQUAL]):
            equal_stretch_compress = getRandomStretchCompress()
            dst_top_right[X] = dst_top_right[X] + equal_stretch_compress
            dst_bottom_right[X] = dst_bottom_right[X] + equal_stretch_compress
        else:
            dst_top_right[X] = dst_top_right[X] + getRandomStretchCompress()
            dst_bottom_right[X] = dst_bottom_right[X] + getRandomStretchCompress()
        del counts_of_corner_occurences[P_TRANSFORMATION[RIGHT]]
    
    elif (counts_of_corner_occurences[P_TRANSFORMATION[RIGHT]] == 1):
        if (P_TRANSFORMATION[TOP_RIGHT] in corners_to_drag):
            dst_top_right[X] = dst_top_right[X] + getRandomStretchCompress()
        else:
            dst_bottom_right[X] = dst_bottom_right[X] + getRandomStretchCompress()
        del counts_of_corner_occurences[P_TRANSFORMATION[RIGHT]]
    
    # ==// BOTTOM \\==
    if (counts_of_corner_occurences[P_TRANSFORMATION[BOTTOM]] == 2):
        if (equalOrUnequal() == P_TRANSFORMATION[EQUAL]):
            equal_stretch_compress = getRandomStretchCompress()
            dst_bottom_left[Y] = dst_bottom_left[Y] + equal_stretch_compress
            dst_bottom_right[Y] = dst_bottom_right[Y] + equal_stretch_compress
        else:
            dst_bottom_left[Y] = dst_bottom_left[Y] + getRandomStretchCompress()
            dst_bottom_right[Y] = dst_bottom_right[Y] + getRandomStretchCompress()
        del counts_of_corner_occurences[P_TRANSFORMATION[BOTTOM]]
    
    elif (counts_of_corner_occurences[P_TRANSFORMATION[BOTTOM]] == 1):
        if (P_TRANSFORMATION[BOTTOM_LEFT] in corners_to_drag):
            dst_bottom_left[Y] = dst_bottom_left[Y] + getRandomStretchCompress()
        else:
            dst_bottom_right[Y] = dst_bottom_right[Y] + getRandomStretchCompress()
        del counts_of_corner_occurences[P_TRANSFORMATION[BOTTOM]]
                
    start_points = np.float32([[start_top_left[X], start_top_left[Y]],
                              [start_top_right[X], start_top_right[Y]],
                              [start_bottom_left[X], start_bottom_left[Y]],
                              [start_bottom_right[X], start_bottom_right[Y]]])    
    
    dst_points = np.float32([[dst_top_left[X], dst_top_left[Y]],
                             [dst_top_right[X], dst_top_right[Y]],
                             [dst_bottom_left[X], dst_bottom_left[Y]],
                             [dst_bottom_right[X], dst_bottom_right[Y]]])
    
    
    M_transformation = cv2.getPerspectiveTransform(start_points, dst_points)    
    dst_transformation = cv2.warpPerspective(image_array, M_transformation, (cols, rows), borderValue=255)

    return dst_transformation