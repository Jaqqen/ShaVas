TOP = 'TOP'
RIGHT = 'RIGHT'
LEFT = 'LEFT'
BOTTOM = 'BOTTOM'

TOP_LEFT = 'TOP_LEFT'
TOP_RIGHT = 'TOP_RIGHT'
BOTTOM_LEFT = 'BOTTOM_LEFT'
BOTTOM_RIGHT = 'BOTTOM_RIGHT'

MAX_Y = 'max_Y'
MAX_X = 'max_X'
MIN_Y = 'min_Y'
MIN_X = 'min_X'

X = 'X'
Y = 'Y'

def getPixelsOfDrawing(image_array):
    drawing_pixels_holder = []

    for row_index, row_values in enumerate(image_array):        
        hasDrawingColor = hasRowBlackPixels(row_values, 0)

        if (hasDrawingColor == True):
            for column_index, column_value in enumerate(row_values):
                if (column_value == 0):
                    drawing_pixels_holder.append((row_index, column_index))

    return drawing_pixels_holder

def getMaxMinCornerValues(image_array):
    global MAX_Y, MAX_X, MIN_Y, MIN_X
    drawing_pixels_holder = getPixelsOfDrawing(image_array)

    max_Y = max(drawing_pixels_holder, key=lambda item: item[0])[0]

    max_X = max(drawing_pixels_holder, key=lambda item: item[1])[1]

    min_Y = min(drawing_pixels_holder, key=lambda item: item[0])[0]

    min_X = min(drawing_pixels_holder, key=lambda item: item[1])[1]

    return {MAX_Y: max_Y,
            MAX_X: max_X,
            MIN_Y: min_Y,
            MIN_X: min_X}

def getCornerDistancesDictionary(dictMaxMinCornerValues, image_array):
    global MAX_Y, MAX_X, MIN_Y, MIN_X
    global TOP, RIGHT, BOTTOM, LEFT
    distance_bottom = dictMaxMinCornerValues[MAX_Y]
    distance_right = dictMaxMinCornerValues[MAX_X]
    distance_top = dictMaxMinCornerValues[MIN_Y]
    distance_left = dictMaxMinCornerValues[MIN_X]

    cols, rows = getShapeInfo(image_array)

    distance_bottom = rows - distance_bottom
    distance_right = cols - distance_right

    # distances from pixel on canvas to its border
    return {BOTTOM: distance_bottom,
            RIGHT: distance_right,
            TOP: distance_top,
            LEFT: distance_left}

def getCornersOfDrawingFrame(dictMaxMinCornerValues):
    global MAX_Y, MAX_X, MIN_Y, MIN_X
    global TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT, X, Y
    # distances from origin
    return {
        TOP_LEFT: {X: dictMaxMinCornerValues[MIN_X],
                   Y: dictMaxMinCornerValues[MIN_Y]},
        TOP_RIGHT: {X: dictMaxMinCornerValues[MAX_X],
                    Y: dictMaxMinCornerValues[MIN_Y]},
        BOTTOM_LEFT: {X: dictMaxMinCornerValues[MIN_X],
                      Y: dictMaxMinCornerValues[MAX_Y]},
        BOTTOM_RIGHT: {X: dictMaxMinCornerValues[MAX_X],
                       Y: dictMaxMinCornerValues[MAX_Y]}
    }

def getShapeInfo(image_array):
    rows, cols = image_array.shape
    return (cols, rows)

def hasRowBlackPixels(row_values, val_to_check_for):
    return any(_val_of_line <= val_to_check_for for _val_of_line in row_values)