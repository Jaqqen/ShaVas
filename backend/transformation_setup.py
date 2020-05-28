import copy
import cv2
import datetime
import math
import os
import pytz
import random
import time


from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from transformation_variants import getTranslationOfImage, getScaleOfImage, getRotationOfImage, getPerspectiveTransformationOfImage
from shavas_logger import logError, logInfo, logSuccess, logDebug

##################################

#* LISTS
SAMPLES_LIST = []
PROCESS_COMBINATION_FILTER_LIST = []
SHAPES_LIST = []
PROCESS_LIST = []
# TRANSFORMATION_FUNCTIONS_LIST = [getTranslationOfImage, getScaleOfImage, getRotationOfImage, getPerspectiveTransformationOfImage]
TRANSFORMATION_FUNCTIONS_LIST = [getPerspectiveTransformationOfImage]

#* THREAD / PROCESS
_TH = 'Thread'
_PRCS = 'Process'
_res = '_res'
_samples_list = '_samples_list'
_shapes_list = '_shapes_list'
_image_index = '_image_index'
_prcs_num = '_prcs_num'

#* TIME_RELATED
START = 'START'
FINISH = 'FINISH'
TIMES = {
    START: None,
    FINISH: None
}

#* OTHERS
TIMEZONE = None
ARE_SAMPLES_GENERATED = None

##################################

def createMultipleSampleWithProcesses(image, iteration_amount, shape_number, performance_method):
    global _res, _samples_list, _shapes_list, _image_index, _prcs_num
    number, method = performance_method

    __samples_list = []
    __shapes_list = []

    for _ in range(iteration_amount):
        created_image = createSample(image)
        if (created_image is not None):
            __samples_list.append(created_image)
            __shapes_list.append(shape_number)

    process_response = {
        _res: f'{method} with image-index: {shape_number} and {method}-number: {number} has finished',
        _image_index: shape_number,
        _prcs_num: number,
        _samples_list: __samples_list,
        _shapes_list: __shapes_list
    }

    return process_response


def createSample(image):
    global TRANSFORMATION_FUNCTIONS_LIST

    result_image = None

    random_amount_of_transformations = random.randint(1, len(TRANSFORMATION_FUNCTIONS_LIST))

    order_of_random_functions_to_use = []
    added_function_indices = []

    for index in range(random_amount_of_transformations):
        while True:
            random_function_index = random.randint(0, len(TRANSFORMATION_FUNCTIONS_LIST) - 1)
            if (random_function_index not in added_function_indices):
                # add random function index to the list to check for
                added_function_indices.append(random_function_index)
                # append the function with the specific index
                order_of_random_functions_to_use.append(TRANSFORMATION_FUNCTIONS_LIST[random_function_index])
                break

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
        logError(f'PASS - TRANSFORMATION ORDER WAS INTERRUPTED: {e}')
        pass

    try:
        if (result_image is not None):
            #print('> \33[92m RESULT_IMAGE SUCCESSFUL \33[0m')
            return result_image
    except Exception as e:
        logError(f'PASS - RESULT_IMAGE WAS NONE: {e}')
        pass


def getCurrentTimeByTimezone(_timezone):
    tz = pytz.timezone(_timezone)

    date_now = datetime.datetime.now(tz)
    time_now = date_now.time()
    f_time_now = time_now.strftime("%H:%M:%S")

    return f_time_now


def getProcessParameters(desired_amount, imgs_per_process):  
    p_needed = math.floor(desired_amount / imgs_per_process)
    p_needed = 1 if (p_needed < 1) else p_needed
    p_needed = 4 if (p_needed > 4) else p_needed

    amount_per_p = math.floor(desired_amount / p_needed)
    last_p_amount = amount_per_p + (desired_amount % p_needed)

    return (p_needed, amount_per_p, last_p_amount)


def getFrontendSamplesList():
    try:
        for prcs in PROCESS_LIST:
            if (prcs.running()):
                logDebug(f'> Entering running Processes.......')
                return (False, getSamplesInformationFromDoneProcesses())

        return (True, getSamplesInformationWhenAllCompleted())
    except Exception as e:
        logError(f'Could not get Samples: {e}')


def getSamplesInformationFromDoneProcesses():
    global PROCESS_LIST
    global PROCESS_COMBINATION_FILTER_LIST
    global _image_index, _prcs_num, _samples_list

    temp_frontend_samples_list = []

    try:
        logDebug(f'>> Entering DONE Processes.......')
        for future_obj in wait(PROCESS_LIST, timeout=1, return_when=FIRST_COMPLETED).done:
            result = future_obj.result()

            PROCESS_COMBINATION_FILTER_LIST = [t for t in (set(tuple(prcs_comb_filter) for prcs_comb_filter in PROCESS_COMBINATION_FILTER_LIST))]
            prcs_combination = (result[_image_index], result[_prcs_num])

            if (not (prcs_combination in  PROCESS_COMBINATION_FILTER_LIST)):
                PROCESS_COMBINATION_FILTER_LIST.append(prcs_combination)
                frontend_batch = {
                    _image_index: result[_image_index],
                    _prcs_num: result[_prcs_num],
                    _samples_list: [result_sample.tolist() for result_sample in result[_samples_list]]
                }
                temp_frontend_samples_list = temp_frontend_samples_list + [frontend_batch]
    except Exception as e:
        logError(f'Problem in Done_Processes: {e}')

    return temp_frontend_samples_list


def getSamplesInformationWhenAllCompleted():
    global PROCESS_LIST
    global SAMPLES_LIST, SHAPES_LIST
    global TIMES, FINISH, START
    global TIMEZONE
    global _image_index, _prcs_num, _samples_list

    frontend_samples_list = getSamplesInformationFromDoneProcesses()

    try:
        TIMES[FINISH] = time.perf_counter()
        logInfo(f'Finished at: {getCurrentTimeByTimezone(TIMEZONE)}')
        logInfo(f'Finished in {round(TIMES[FINISH]-TIMES[START], 3)} seconds')
        for future_obj in as_completed(PROCESS_LIST):
            result = future_obj.result()
            for result_key in result:
                if (result_key == _res):
                    logSuccess(f'{result_key}: {result[result_key]}')
            SAMPLES_LIST = SAMPLES_LIST + result[_samples_list]
            SHAPES_LIST = SHAPES_LIST + result[_shapes_list]
    except Exception as e:
        logError(f'Problem in Completed Processes: {e}')

    return frontend_samples_list


def setAndStartProcessesByAmount(desired_amount, image_list, timezone, imgs_per_process):
    global TIMES, START
    global PROCESS_LIST
    global _PRCS, _res, _samples_list, _shapes_list
    global TIMEZONE
    PROCESS_LIST.clear()
    SAMPLES_LIST.clear()
    SHAPES_LIST.clear()
    ARE_SAMPLES_GENERATED = False
    PROCESS_COMBINATION_FILTER_LIST.clear()

    TIMEZONE = timezone
    p_needed, amount_per_p, last_p_amount = getProcessParameters(desired_amount, imgs_per_process)

    TIMES[START] = time.perf_counter()
    logInfo(f'Started at: {getCurrentTimeByTimezone(timezone)}')

    for index, image in enumerate(image_list):
        for i in range(p_needed):
            if (i < p_needed-1):
                PROCESS_LIST.append(ProcessPoolExecutor().submit(createMultipleSampleWithProcesses, image, amount_per_p, index, (i, _PRCS)))
            else:
                PROCESS_LIST.append(ProcessPoolExecutor().submit(createMultipleSampleWithProcesses, image, last_p_amount, index, (i, _PRCS)))

    for prcs in PROCESS_LIST:
        logInfo(f'{prcs}')
