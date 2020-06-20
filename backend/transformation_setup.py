import copy
import cv2
import datetime
import math
import os
import pytz
import random
import time
import shutil

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from transformation_variants import getTranslationOfImage, getScaleOfImage, getRotationOfImage, getPerspectiveTransformationOfImage
from shavas_logger import logError, logInfo, logSuccess, logDebug

##################################

#* LISTS
SAMPLES_LIST = []
SHAPES_LIST = []
PROCESS_LIST = []
TRANSFORMATION_FUNCTIONS_LIST = [getPerspectiveTransformationOfImage, getTranslationOfImage, getScaleOfImage, getRotationOfImage]
PROCESS_COMBINATION_FILTER_SET = set()
SAVED_BATCH_INFO_LIST = []

#* THREAD / PROCESS
_TH = 'Thread'
_PRCS = 'Process'
_res = '_res'
_samples_list = '_samples_list'
_shapes_list = '_shapes_list'
_image_index = '_image_index'
_prcs_num = '_prcs_num'
_path = '_path'
_hasBeenRead = '_hasBeenRead'
BATCH_SIZE = 1000
MAX_BATCHES_PER_IMG = 0

#* TIME_RELATED
START = 'START'
FINISH = 'FINISH'
TIMES = {
    START: None,
    FINISH: None
}

#* OTHERS
TIMEZONE = None
SAMPLES_DIR = './samplesDir'
RESPONSES_DIR = './responses'

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
    global PROCESS_LIST, SAVED_BATCH_INFO_LIST, MAX_BATCHES_PER_IMG

    try:
        for prcs in PROCESS_LIST:
            if (prcs.running() or
                any(child_dict[_hasBeenRead] == False for child_dict in SAVED_BATCH_INFO_LIST) or
                len(SAVED_BATCH_INFO_LIST) < (MAX_BATCHES_PER_IMG * 2)):
                logDebug(f'> Entering DONE Processes.......')
                return (False, getSamplesInformationFromDoneProcesses())
            else:
                return (True, getSamplesInformationWhenAllCompleted())
    except Exception as e:
        logError(f'Could not get Samples: {e}')


def getSamplesInformationFromDoneProcesses():
    global PROCESS_LIST, BATCH_SIZE
    global PROCESS_COMBINATION_FILTER_SET, SAVED_BATCH_INFO_LIST
    global SAMPLES_DIR
    global _image_index, _prcs_num, _samples_list, _path, _hasBeenRead

    temp_frontend_samples_batches = []

    try:
        for future_obj in wait(PROCESS_LIST, timeout=1, return_when=FIRST_COMPLETED).done:
            result = future_obj.result()
            current_image_index = result[_image_index]
            current_prcs_num = result[_prcs_num]

            img_prcs_comb = (current_image_index, current_prcs_num)

            if (not (img_prcs_comb in PROCESS_COMBINATION_FILTER_SET)):
                PROCESS_COMBINATION_FILTER_SET.add(img_prcs_comb)

                res_samples_list = result[_samples_list]
                batch_num = 0

                for cur_step_val in range(0, len(res_samples_list), BATCH_SIZE):
                    current_result_samples_list_batch = res_samples_list[cur_step_val:cur_step_val+BATCH_SIZE]

                    SAVED_BATCH_INFO_LIST.append(saveSamples(current_result_samples_list_batch, current_image_index, current_prcs_num, batch_num))
                    batch_num = batch_num + 1

                print('---')
                logDebug(f'> current_image_index:  {current_image_index} | current_prcs_num: {current_prcs_num}')


        amount_returning_batches = 0

        try:
            if (any(child_dict[_hasBeenRead] == False for child_dict in SAVED_BATCH_INFO_LIST)):

                for saved_batch_info in SAVED_BATCH_INFO_LIST:
                    if (amount_returning_batches <= 4 and saved_batch_info[_hasBeenRead] == False):
                        current_image_index = saved_batch_info[_image_index]
                        current_path = saved_batch_info[_path]

                        current_frontend_samples_list = []
                        for image_name in os.listdir(current_path):
                            image_path = f'{current_path}/{image_name}'
                            sample = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

                            current_frontend_samples_list.append(sample.tolist())

                        frontend_batch = {
                            _samples_list: current_frontend_samples_list,
                            _image_index: current_image_index,
                        }

                        temp_frontend_samples_batches.append(frontend_batch)

                        saved_batch_info[_hasBeenRead] = True

                        amount_returning_batches = amount_returning_batches + 1
                        logDebug(f'amount_returning_batches: {amount_returning_batches}')

        except Exception as e:
            if (isinstance(e, KeyError)):
                pass
            else:
                logError(f'Error when accessing batches: {e}')
                pass

    except Exception as e:
        logError(f'Problem in Done_Processes: {e}')

    return temp_frontend_samples_batches


def getSamplesInformationWhenAllCompleted():
    global PROCESS_LIST, SAVED_BATCH_INFO_LIST
    global SAMPLES_LIST, SHAPES_LIST
    global TIMES, FINISH, START
    global TIMEZONE
    global _image_index, _prcs_num, _samples_list
    SAMPLES_LIST.clear()
    SHAPES_LIST.clear()
    SAVED_BATCH_INFO_LIST.clear()

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
    global PROCESS_LIST, BATCH_SIZE, MAX_BATCHES_PER_IMG
    global _PRCS, _res, _samples_list, _shapes_list, _prcs_num
    global TIMEZONE, SAMPLES_DIR
    global PROCESS_COMBINATION_FILTER_SET
    PROCESS_LIST.clear()
    PROCESS_COMBINATION_FILTER_SET = set()


    try:
        for child_dir in os.listdir(SAMPLES_DIR):
            child_path = f'{SAMPLES_DIR}/{child_dir}'
            shutil.rmtree(child_path, ignore_errors=True)

        for child_file in os.listdir(RESPONSES_DIR):
            child_file_path = f'{RESPONSES_DIR}/{child_file}'
            os.remove(child_file_path)

        TIMEZONE = timezone
        p_needed, amount_per_p, last_p_amount = getProcessParameters(desired_amount, imgs_per_process)

        batches_per_prcs = math.ceil((desired_amount/p_needed)/BATCH_SIZE)
        MAX_BATCHES_PER_IMG = batches_per_prcs * p_needed

        MAX_BATCHES_PER_IMG = math.ceil(desired_amount/BATCH_SIZE)
        logInfo(f'len_of_batches_in_total: {MAX_BATCHES_PER_IMG * 2}')

        TIMES[START] = time.perf_counter()

        start_time = getCurrentTimeByTimezone(timezone)
        logInfo(f'Started at: {start_time}')

        for index, image in enumerate(image_list):
            for i in range(p_needed):
                if (i < p_needed-1):
                    PROCESS_LIST.append(ProcessPoolExecutor().submit(createMultipleSampleWithProcesses, image, amount_per_p, index, (i, _PRCS)))
                else:
                    PROCESS_LIST.append(ProcessPoolExecutor().submit(createMultipleSampleWithProcesses, image, last_p_amount, index, (i, _PRCS)))

        for prcs in PROCESS_LIST:
            logInfo(f'{prcs}')

        return {
            'startTime': start_time,
            'batchesPerImg': MAX_BATCHES_PER_IMG,
            'prcsStartedPerImg': p_needed * 2,
            'hasBeenStarted': True
        }
    except Exception as e:
        return {
            'startTime': None,
            'batchesPerImg': 0,
            'prcsStartedPerImg': 0,
            'hasBeenStarted': False
        }


def saveSamples(current_result_samples_list_batch, current_image_index, current_prcs_num, batch_num):
    global SAMPLES_DIR
    global _image_index, _path, _hasBeenRead
    current_image_path = f'{SAMPLES_DIR}/{current_image_index}'

    if (not os.path.isdir(current_image_path)):
        os.mkdir(current_image_path)

    batch_dir_name = f'Prcs-{current_prcs_num}_BATCH_{batch_num}'
    current_batch_path = f'{current_image_path}/{batch_dir_name}'
    os.mkdir(current_batch_path)

    for index, sample in enumerate(current_result_samples_list_batch):
        file_path = f'{current_batch_path}/IMG_{index}.png'
        cv2.imwrite(file_path, sample)

    return {
        _image_index: current_image_index,
        _path: current_batch_path,
        _hasBeenRead: False
    }