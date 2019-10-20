import cv2

PIXELVALUETOCONVERTTO = 100


def getShapeInfo(image_array):
    rows, cols = image_array.shape

    return (cols, rows)


# returns 'True' if row is white
def checkAllValuesOfRow(line_as_list, _val):
    return all(x == _val for x in line_as_list)


# returns 'True' if any pixel in row is equal to _val
def checkForAnyValueOfRow(line_as_list, _val):
    return any(x <= _val for x in line_as_list)


# converts all values that are lower that pure white (value == 255) to
# a lower value (value = PIXELVALUETOCONVERTTO) to extinguish between
# pure black pixels, pure white pixels and the pixels of the drawing
def convertPixelValues(image_array):
    for r_index, line in enumerate(image_array):
        rowIsWhite = checkAllValuesOfRow(line, 255)

        # if row is not completely white
        if (rowIsWhite == False):
            for c_index, value in enumerate(line):
                if (value < 255):
                    # turn pixel nearly black
                    image_array[r_index, c_index] = PIXELVALUETOCONVERTTO

    return image_array


# converts all pure Black values (value == 0) to white (value = 255)
def convertPixelsToWhite(image_array):
    for r_index, line in enumerate(image_array):
        hasBlack = checkForAnyValueOfRow(line, 10)

        if (hasBlack == True):
            for c_index, value in enumerate(line):
                if (value < PIXELVALUETOCONVERTTO - 10
                        or value > PIXELVALUETOCONVERTTO + 10):
                    # turn pixel into white
                    image_array[r_index, c_index] = 255

    return image_array


# extract all pixels that have the pixel-value of the drawing
# (value == PIXELVALUETOCONVERTTO)
def getPixelsOfDrawing(image):
    # will hold the corner values of the image frame (so the corners of the frame that only contains the drawing)
    pixel_holder = []

    for r_index, line in enumerate(image):
        hasDrawingPixel = checkForAnyValueOfRow(line, PIXELVALUETOCONVERTTO)

        if (hasDrawingPixel == True):
            for c_index, value in enumerate(line):
                if (value == PIXELVALUETOCONVERTTO):
                    pixel_holder.append((r_index, c_index))

    return pixel_holder


# First, the image is read in grayscale (imread(_PATH_, 0))
# Secondly, the shape of the image needs to be detected so that we can downscale the dimensions
# Thirdly, the newly calculated dimensions are used to resize the image via cv2
# Finally, the resized image-array is returned
def prepareImageBeforeConversion(PATHTOIMG):
    canvas_drawing = cv2.imread(PATHTOIMG, 0)
    shape = canvas_drawing.shape

    n_dim_values = []

    for dimension in shape:
        n_dim_values.append(int(dimension * 0.25))

    # needs to be tuple to resize image
    new_dim = (n_dim_values[1], n_dim_values[0])
    canvas_drawing = cv2.resize(canvas_drawing,
                                new_dim,
                                interpolation=cv2.INTER_AREA)

    return canvas_drawing


# this returns the min and max values of the pixel_holder-list
# kinda extracting the x and y coordinates of the frame in which
# the drawing is contained
def getCalcOfMaxMinValuesOfPixelHolder(image):
    pixel_holder = getPixelsOfDrawing(image)

    #max row
    max_row = max(pixel_holder, key=lambda item: item[0])[0]
    #print(max(pixel_holder, key=lambda item: item[0])[0])
    #max col
    max_col = max(pixel_holder, key=lambda item: item[1])[1]
    #print(max(pixel_holder, key=lambda item: item[1])[1])
    #min row
    min_row = min(pixel_holder, key=lambda item: item[0])[0]
    #print(min(pixel_holder, key=lambda item: item[0])[0])
    #min col
    min_col = min(pixel_holder, key=lambda item: item[1])[1]
    #print(min(pixel_holder, key=lambda item: item[1])[1])

    return [max_row, max_col, min_row, min_col]


# returns the distances from the borders
# distances[0] - distance to bottom border
# distances[1] - distance to right border
# distances[2] - distance to top border
# distances[3] - distance to left border
def getDistances(listOfMaxAndMinValues, image_array):
    distances = listOfMaxAndMinValues

    cols, rows = getShapeInfo(image_array)

    distances[0] = rows - distances[0]
    distances[1] = cols - distances[1]

    return distances


# returns the corners of the drawing frame as a list
# needs to be like this when constructing the matrix for stretching
# and compressing
def getCornersOfDrawingFrame(listOfMaxAndMinValues):
    maxMinValues = listOfMaxAndMinValues

    corners = [[maxMinValues[3], maxMinValues[2]],
               [maxMinValues[1], maxMinValues[2]],
               [maxMinValues[3], maxMinValues[0]],
               [maxMinValues[1], maxMinValues[0]]]
    return corners