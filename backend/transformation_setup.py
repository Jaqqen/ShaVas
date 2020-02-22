import copy, random, math, threading, cv2, traceback
from transformation_variants import getTranslationOfImage, getScaleOfImage, getRotationOfImage, getPerspectiveTransformationOfImage

thread_amount = 0
SAMPLES_LIST = []
SHAPE_LIST = []
THREAD_LIST = []
TRANSFORMATION_FUNCTIONS_LIST = [getTranslationOfImage, getScaleOfImage, getRotationOfImage, getPerspectiveTransformationOfImage]

def createMultipleSample(image, iteration_amount, shape_number):
    global SAMPLES_LIST, SHAPE_LIST

    for _ in range(iteration_amount):
        created_image = createSample(image)
        if (created_image is not None):
            SAMPLES_LIST.append(created_image)
            SHAPE_LIST.append(shape_number)

def createSample(image):
    global TRANSFORMATION_FUNCTIONS_LIST
    result_image = None

    # get random amount of transformations, results = 1 - n
    random_amount_of_transformations = random.randint(1, len(TRANSFORMATION_FUNCTIONS_LIST))

    # create order of transformations
    order_of_random_functions_to_use = []
    added_function_indices = []

    for index in range(random_amount_of_transformations):
        random_function_index = random.randint(0, len(TRANSFORMATION_FUNCTIONS_LIST) - 1)

        while True:
            if (random_function_index not in added_function_indices):
                # add random function index to the list to check for
                added_function_indices.append(random_function_index)
                # append the function with the specific index
                order_of_random_functions_to_use.append(TRANSFORMATION_FUNCTIONS_LIST[random_function_index])
            else:
                random_function_index = random.randint(0, len(TRANSFORMATION_FUNCTIONS_LIST) - 1)
                continue
            break

    # try to execute transformation order
    try:
        transformed_image = None
        
        for index, function in enumerate(order_of_random_functions_to_use):
            # if its the last iteration
            if (index == (len(order_of_random_functions_to_use) - 1)):
                # if the image was not transformed because there might be just one iteration
                if (transformed_image is not None):
                    result_image = function(transformed_image)
                else:
                    result_image = function(image)
            # if first iteration than use image parameter
            elif (index == 0):
                transformed_image = function(image)
            # if its neither the first nor the last iteration
            else:
                transformed_image = function(transformed_image)

    except Exception as e:
        print('> \33[91m PASS - TRANSFORMATION ORDER WAS INTERRUPTED \33[0m')
        pass

    # try to return the transformed image
    # there are cases where the image is not transformed at all
    try:
        if (result_image is not None):
            print('> \33[92m RESULT_IMAGE WAS SAVED \33[0m')
            return result_image
    except Exception as e:
        print('> \33[90m PASS - RESULT_IMAGE WAS NONE \33[0m')
        pass


def createThreadForSamplesCreation(desired_amount, image_list):
    global THREAD_LIST
    setToInitialState()

    threads_needed, iteration_amount, rest = getThreadParameters(desired_amount)

    image_0, image_1 = image_list

    for index, image in enumerate(image_list):
        for i in range(threads_needed):
            amount = rest if (not (i < threads_needed-1) and (rest > 0)) else iteration_amount
            thread = threading.Thread(target=createMultipleSample,
                                      args=[image, amount, index])
            thread.start()
            THREAD_LIST.append(thread)

    print(f'LEN OF THREADS IN LIST: {len(getThreadList())}')


def getSamplesListAsJson():
    global SAMPLES_LIST

    samples_list_copy = copy.deepcopy(SAMPLES_LIST)
    frontend_json = []

    for index, sample in enumerate(samples_list_copy):
        try:
            path = '/Users/jaqqen/ShaVas/backend/testingIMG/' + str(index) + '.png'
            cv2.imwrite(path, sample)
            cv2.waitKey(0)
        except Exception as e:
            print('Could not save image')

        frontend_json.append(sample.tolist())

    print(f'LEN OF SAMPLES IN LIST: {len(SAMPLES_LIST)}')

    return frontend_json

def getThreadList():
    global THREAD_LIST
    return THREAD_LIST

def getThreadParameters(desired_amount):
    divider = 100 if (desired_amount <= 1000) else 1000

    th_needed = math.floor(desired_amount / divider)
    rest = desired_amount % divider
    th_needed = th_needed + 1 if (rest > 0) else th_needed
    return (th_needed, divider, rest)

def setToInitialState():
    global thread_amount
    global SAMPLES_LIST, SHAPE_LIST, THREAD_LIST

    thread_amount = 0
    SAMPLES_LIST.clear()
    SHAPE_LIST.clear()
    THREAD_LIST.clear()