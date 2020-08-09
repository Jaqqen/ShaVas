import base64
import cv2
import json
import os
import time

from flask import Flask, jsonify, request, Response
from image_preperation import appendPreparedImage, saveImageToPath
from tensorflow.keras.utils import normalize

from neural_network import *
from transformation_setup import *
from shavas_logger import logDebug, logError, logInfo, logSuccess

import numpy as np
import tensorflow as tf


app = Flask(__name__)


PREPARED_SHAVAS_INPUT_IMAGES_PATH_PREFIX = './prepared_shavas_input_images/prepared_shavas_image_'
PREPARED_SHAVAS_INPUT_IMAGES_PATH_FILETYPE = '.pickle'

IMAGE_PATH_PREFIX = '../drawnImages/'
DATA_0_KEY = 'data0'
DATA_1_KEY = 'data1'
SAMPLE_AMOUNT_KEY = 'sampleAmount'

IMGS_PER_PROCESS = 1000

print('!!!!!!!!!!!!!!!!!!!!!!!!!!')
print('!!!!!!!!START MAIN!!!!!!!!')
print('!!!!!!!!!!!!!!!!!!!!!!!!!!')


# takes two base64-strings and saves them as images
# takes the amount of samples that should be generated
# async action: creates multiple different samples
@app.route('/sendCanvas', methods=['POST'])
def sendCanvas():
    global DATA_0_KEY, DATA_1_KEY
    global IMAGE_PATH_PREFIX
    global SAMPLE_AMOUNT_KEY, IMGS_PER_PROCESS

    json_Obj = request.get_json()

    json_images = [json_Obj[DATA_0_KEY], json_Obj[DATA_1_KEY]]

    image_list = []

    for index, drawing in enumerate(json_images):
        header, encoded = drawing.split(",", 1)
        decoded_data = base64.b64decode(encoded)
        drawing_path = IMAGE_PATH_PREFIX + 'canvasImage_' + str(index) + '.png'

        saveImageToPath(decoded_data, drawing_path)

        image_list.append(appendPreparedImage(drawing_path))

    response = setAndStartProcessesByAmount(json_Obj[SAMPLE_AMOUNT_KEY], image_list, 'Europe/Berlin', IMGS_PER_PROCESS)

    return jsonify(response), 200


# gets the current samples list as lists in list for json.dump
@app.route('/getSamples', methods=['GET'])
def getSamples():
    js = {
        "sample_list_batches": [],
        "samples_created": False
    }
    try:
        _are_samples_created, frontend_content = getFrontendSamplesList()

        if (isinstance(frontend_content, dict)):
            js = {
                "samples_end_response": frontend_content,
                "samples_created": _are_samples_created
            }
        else:
            js = {
                "sample_list_batches": frontend_content,
                "samples_created": _are_samples_created
            }
    except Exception as e:
        logError(f'COULD NOT GET SAMPLES_INFORMATION: {e}')

    try:
        current_frontend_json = json.dumps(js)
    except Exception as e:
        logError(f"Couldn't dump{e}")
        current_frontend_json = None


    res_file_path = f"responses/response_{getCurrentTimeByTimezone('Europe/Berlin')}.json"
    with open(res_file_path, "w") as res_file: 
        res_file.write(current_frontend_json) 

    return Response(current_frontend_json, mimetype='application/json'), 200


# identifies the image
@app.route('/identify', methods=['POST'])
def identify():
    data_i = request.get_json()['dataI']
    header, encoded = data_i.split(",", 1)
    decoded_data = base64.b64decode(encoded)
    path = IMAGE_PATH_PREFIX + 'identifyerImage.png'
    saveImageToPath(decoded_data,path)

    image = getImageFromPath(path)

    predictions = identifyImageProbabilities(image, conv2d=True)

    return Response(json.dumps(predictions.tolist()),mimetype='application/json'), 200


@app.route('/buildNeuralNetwork', methods=['GET'])
def buildNeuralNetwork():
    start_information = startBuildNeuralNetwork('Europe/Berlin')
    logDebug(f'BUILD_INFO: {start_information}')

    return Response(json.dumps(start_information), mimetype='application/json'), 200


@app.route('/hasNeuralNetworkBuildFinished', methods=['GET'])
def hasNeuralNetworkBuildFinished():
    hasBeenBuilt = { 'hasBeenBuilt': getNeuralNetworkResult() }

    return Response(json.dumps(hasBeenBuilt), mimetype='application/json'), 200


if __name__ == '__main__':
    app.run(debug=True, threaded=True)