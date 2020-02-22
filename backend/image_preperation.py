import cv2

BLACK = 0
PURE_WHITE = 255
RESIZE_MULTIPLYER = 0.125


def appendPreparedImage(image_path):
    canvas_drawing = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    resized_image = resizeImageWithNewDimensions(canvas_drawing)
    return setDrawingPixelsBlack(resized_image)


def isRowWhite(row_values, val_to_check_for):
    return all(_val_of_line == val_to_check_for for _val_of_line in row_values)


def resizeImageWithNewDimensions(image):
    global RESIZE_MULTIPLYER

    rows, columns = image.shape
    new_dimensions = (int(columns * RESIZE_MULTIPLYER),
                      int(rows * RESIZE_MULTIPLYER))

    return cv2.resize(image, new_dimensions, interpolation=cv2.INTER_AREA)


def setDrawingPixelsBlack(image_array):
    global BLACK, PURE_WHITE

    for row_index, row_values in enumerate(image_array):
        is_row_white = isRowWhite(row_values, PURE_WHITE)

        if (is_row_white == False):
            for column_index, column_value in enumerate(row_values):
                if (column_value < PURE_WHITE):
                    image_array[row_index, column_index] = BLACK

    return image_array


def saveImagesToPath(decoded_data, image_path):
    with open(image_path, 'wb') as image_file:
        image_file.write(decoded_data)