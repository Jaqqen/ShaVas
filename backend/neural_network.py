import random
import pickle
import os
import cv2

import numpy as np

from tensorflow.keras.utils import normalize
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Activation, Flatten, Dropout, Conv2D, MaxPooling2D
from tensorflow.nn import relu, softmax, leaky_relu
from concurrent.futures import ProcessPoolExecutor, as_completed, wait, FIRST_COMPLETED

from shavas_logger import logError, logInfo, logSuccess, logDebug
from transformation_setup import getCurrentTimeByTimezone
from tensorflow.keras.backend import set_floatx

set_floatx('float64')

SAMPLES_PICKLE_PATH = './neural_network_data/samples.pickle'
SHAPES_PICKLE_PATH = './neural_network_data/shapes.pickle'
MODEL_PATH = './neural_network_data/sample_shape_model.h5'

NEURAL_NETWORK_RESULT = None

DIMENSION = 100

_model = '_model'
_m_hist = '_m_hist'
_is_training_done = '_is_training_done'


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def buildNeuralNetworkModel(conv2d=False):
    global SAMPLES_PICKLE_PATH, SHAPES_PICKLE_PATH, MODEL_PATH
    global DIMENSION
    global _model, _y
    global _m_hist, _is_training_done


    samples_list = loadPickleDataFromPath(SAMPLES_PICKLE_PATH)
    shapes_list = loadPickleDataFromPath(SHAPES_PICKLE_PATH)

    merged_tuple_list = []

    for index, sample in enumerate(samples_list):
        merged_tuple_list.append([sample, shapes_list[index]])

    random.shuffle(merged_tuple_list)

    X = []
    y = []

    for sample, shape in merged_tuple_list:
        X.append(sample)
        y.append(shape)

    X = np.asarray(X)
    y = np.asarray(y)

    X_normalized = normalize(X, axis=1)

    model = Sequential()

    logDebug('BEFORE LAYERS')

    if (conv2d):
        logDebug('BEFORE CONV2D')
        X_normalized = X_normalized.reshape(-1, DIMENSION, DIMENSION, 1)
        logDebug('AFTER NORMALIZE')

        model.add(Conv2D(60, strides=(3,3), kernel_size=3, activation=relu, input_shape=(DIMENSION, DIMENSION, 1)))
        logDebug('AFTER FIRST CONV2D')
        model.add(MaxPooling2D(pool_size=(2,2)))
        logDebug('AFTER FIRST MAXPOOLING')

        model.add(Dropout(0.5))
        logDebug('AFTER DROPOUT')

        model.add(Conv2D(30, strides=(3,3), kernel_size=3, activation=relu, input_shape=(DIMENSION, DIMENSION, 1)))
        logDebug('AFTER SECOND CONV2D')
        model.add(MaxPooling2D(pool_size=(2,2)))
        logDebug('AFTER SECOND MAXPOOLING')

        logDebug('BEFORE FLATTEN IN CONV2D')
        model.add(Flatten())
        model.add(Dense(30, activation=relu, kernel_constraint=None, bias_constraint=None))
        logDebug('AFTER FIRST DENSE')

        model.add(Dense(2, activation=softmax, kernel_constraint=None, bias_constraint=None))
        logDebug('AFTER SECOND DENSE')
    else:
        model.add(Flatten())
        model.add(Dense(50, activation=relu, kernel_constraint=None, bias_constraint=None))
        model.add(Dropout(.1))
        model.add(Dense(50, activation=relu, kernel_constraint=None, bias_constraint=None))
        model.add(Dropout(.3))
        model.add(Dense(2, activation=softmax, kernel_constraint=None, bias_constraint=None))

    logDebug('BEFORE COMPILE')

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='Adam',
                  metrics=['accuracy'])

    logDebug('BEFORE FIT')
    try:
        if (conv2d):
            # m_hist = model.fit(X_normalized, y, batch_size=200, epochs=12, validation_split=0.3, workers=4)
            model.fit(X_normalized, y, batch_size=200, epochs=12, validation_split=0.3, workers=4)
        else:
            # m_hist = model.fit(X_normalized, y, batch_size=200, epochs=12, validation_split=0.2)
            model.fit(X_normalized, y, batch_size=200, epochs=12, validation_split=0.2)
        model.save(MODEL_PATH)
        logDebug("Trained model")
        # return {
        #     _m_hist: m_hist,
        #     _is_training_done: True
        # }
        return True
    except (RuntimeError, ValueError) as e:
        print('===> Error occured - neural_network.py', e)
        # return {
        #     _m_hist: None,
        #     _is_training_done: False
        # }
        return False


def loadPickleDataFromPath(path):
    try:
        pickle_in = open(path, 'rb')
        return pickle.load(pickle_in)
    except Exception as e:
        print(f'Error in loading pickle: {e}')


def identifyImageProbabilities(image_list, conv2d=False):
    global MODEL_PATH, DIMENSION

    model = load_model(MODEL_PATH)

    if (not isinstance(image_list, list)):
        image = cv2.resize(image_list, (DIMENSION, DIMENSION), interpolation = cv2.INTER_AREA)
        image_list = [image]

    image_list_as_array = np.asarray(image_list)
    image_list_as_array = normalize(image_list_as_array, axis=1)


    if (conv2d):
        return model.predict(image_list_as_array.reshape(-1, DIMENSION, DIMENSION, 1))
    else:
        return model.predict(image_list_as_array)


def getImageFromPath(image_path):
    global DIMENSION

    if (isinstance(image_path, list)):
        image_paths = []
        for path in image_path:
            canvas_drawing = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            resized_canvas = cv2.resize(canvas_drawing, (DIMENSION, DIMENSION), interpolation=cv2.INTER_AREA)
            image_paths.append(resized_canvas)

        return image_paths
    else:
        canvas_drawing = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        return cv2.resize(canvas_drawing, (DIMENSION, DIMENSION), interpolation=cv2.INTER_AREA)

def startBuildNeuralNetwork(timezone):
    global NEURAL_NETWORK_RESULT

    try:
        nn_start_time = getCurrentTimeByTimezone(timezone)
        # has_been_built = buildNeuralNetworkModel(conv2d=True)
        NEURAL_NETWORK_RESULT = None

        NEURAL_NETWORK_RESULT = ProcessPoolExecutor(max_workers=4).submit(buildNeuralNetworkModel, conv2d=True)

        return {
            'startTime': nn_start_time,
            'hasBeenStarted': True
        }
        # return {
        #     'startTime': nn_start_time,
        #     'hasBeenBuilt': has_been_built
        # }
    except Exception as e:
        logError(f'Failed to start Process: {e}')
        return {
            'startTime': None,
            'hasBeenStarted': False
        }
        # return {
        #     'startTime': None,
        #     'hasBeenBuilt': False
        # }


def getNeuralNetworkResult():
    global NEURAL_NETWORK_RESULT
    global MODEL_PATH
    global _m_hist, _is_training_done

    try:
        # nn_result = False
        # # for future_obj in wait([NEURAL_NETWORK_RESULT], timeout=5, return_when=FIRST_COMPLETED).done:
        # for future_obj in as_completed([NEURAL_NETWORK_RESULT], timeout=5):
        #     result = future_obj.result()

        #     logDebug(f'{_is_training_done}: {result[_is_training_done]}')

        #     nn_result = result[_is_training_done]

        #     logDebug(f'{result[_m_hist]}')
        # return nn_result

        if NEURAL_NETWORK_RESULT.running():
            return False
        else:
            return NEURAL_NETWORK_RESULT.result()
    except Exception as e:
        logError(f"Couldn't get result: {e}")
        return False