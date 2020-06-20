import base64
import cv2
import json
import os
import time

from flask import Flask, jsonify, request, Response
from image_preperation import appendPreparedImage, saveImageToPath
# from neural_network import create_training_data_conv, getModelName
from tensorflow.keras.utils import normalize
from transformation_setup import *
from shavas_logger import *

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
@app.route('/send_canvas', methods=['POST'])
def send_canvas():
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

    setAndStartProcessesByAmount(json_Obj[SAMPLE_AMOUNT_KEY], image_list, 'Europe/Berlin', IMGS_PER_PROCESS)

    return jsonify('Saved Images and generation of data has started, please wait.'), 200


#! To be added later on
# checks if a neural network model already exists
@app.route('/if_neural_network', methods=['GET'])
def if_neural_network():
    path = './' + getModelName()
    if (os.path.isfile(path)):
        return jsonify(True), 200
    else:
        return jsonify(False), 201


# gets the current samples list as lists in list for json.dump
@app.route('/getSamples', methods=['GET'])
def getSamples():
    are_samples_created = False
    frontend_samples_list = None
    try:
        logDebug(f'Getting Samples........')
        _are_samples_created, _frontend_samples_list = getFrontendSamplesList()
        frontend_samples_list = _frontend_samples_list
        are_samples_created = _are_samples_created

    except Exception as e:
        logError(f'COULD NOT GET SAMPLES_INFORMATION: {e}')
        pass

    js = {
        "sample_list_batches": frontend_samples_list,
        "samples_created": are_samples_created
        }

    current_frontend_json = None
    try:
        current_frontend_json = json.dumps(js)
    except Exception as e:
        logError(f"Couldn't dump{e}")


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
    with open(path, 'wb') as f:
        f.write(decoded_data)

    # image = supportFunctions.prepareImageBeforeConversion(path)
    # image = image / 255.0
    image_list = []
    image_list.append(image)
    image_list = np.asarray(image_list)
    image_list = normalize(image_list, axis=1)
    my_model = tf.keras.models.load_model('./shape_canvas_model.h5')
    # image_reshaped = np.array(image).reshape(-1, image.shape[0],
    #                                          image.shape[1], 1)
    # predictions = my_model.predict(image_reshaped)
    predictions = my_model.predict(image_list)

    return Response(json.dumps(predictions.tolist()),
                    mimetype='application/json'), 200


#! To be added later on
# start with existing NN
@app.route('/start_with_existing_nn', methods=['GET'])
def start_with_existing_nn():
    shape_one_image = None
    shape_two_image = None
    for index, image_name in enumerate(os.listdir(IMAGE_PATH_PREFIX)):
        if (image_name == 'canvasImage_0.png'):
            path = IMAGE_PATH_PREFIX + image_name
            image = cv2.imread(path, 0)
            shape_one_image = image.tolist()
        elif (image_name == 'canvasImage_1.png'):
            path = IMAGE_PATH_PREFIX + image_name
            image = cv2.imread(path, 0)
            shape_two_image = image.tolist()

    # sample_list = getSamplesListForJSON()

    js = {
        "shape_one_image": shape_one_image,
        "shape_two_image": shape_two_image,
        "sample_list": sample_list,
    }
    return Response(json.dumps(js), mimetype='application/json'), 200


if __name__ == '__main__':
    app.run(debug=True, threaded=True)