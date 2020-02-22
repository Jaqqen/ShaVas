from flask import Flask, jsonify, request, Response
from image_preperation import appendPreparedImage, saveImagesToPath
from neural_network import create_training_data_conv, getModelName
from tensorflow.keras.utils import normalize
from threading import Thread
from transformation_setup import createThreadForSamplesCreation, getSamplesListAsJson, getThreadList

import image_preperation as img_prep
import numpy as np
import tensorflow as tf

import base64, cv2, json, os, time

app = Flask(__name__)

SHAVAS_INPUT_IMAGES_PATH = '/Users/jaqqen/JupyterRoot/ShaVas_2/SHAVAS_INPUT_IMAGES/'
PREPARED_SHAVAS_INPUT_IMAGES_PATH_PREFIX = './prepared_shavas_input_images/prepared_shavas_image_'
PREPARED_SHAVAS_INPUT_IMAGES_PATH_FILETYPE = '.pickle'

IMAGE_PATH_PREFIX = '../drawnImages/'
DATA_0_KEY = 'data0'
DATA_1_KEY = 'data1'
SAMPLE_AMOUNT_KEY = 'sampleAmount'

# temporarily holds holds both canvas-input data
temp_data_list = []

# holds both images - prepareImageBeforeConversion and convertPixelValues
# also is used when createMultipleSamples
image_list = []

# is used to tell the frontend that all samples have been created and the
# neural network has been build
samples_and_nn_isDone = False

print('!!!!!!!!!!!!!!!!!!!!!!!!!!')
print('!!!!!!!!START MAIN!!!!!!!!')
print('!!!!!!!!!!!!!!!!!!!!!!!!!!')


# Clears data when starting application or refreshing
@app.route('/clear_datalist', methods=['GET'])
def clear_datalist():
    global samples_and_nn_isDone

    temp_data_list.clear()
    image_list.clear()
    samples_and_nn_isDone = False

    response_str = (
        '>>> Cleared datalist amount: ' + str(len(temp_data_list)),
        '>>> Cleared image_list: ' + str(len(image_list)),
        '>>> Cleared samples_and_nn_isDone: ' + str(samples_and_nn_isDone),
    )
    return jsonify(response_str), 200


# takes two base64-strings and saves them as images
# takes the amount of samples that should be generated
# async action: creates multiple different samples
@app.route('/send_canvas', methods=['POST'])
def send_canvas():
    global DATA_0_KEY, DATA_1_KEY, IMAGE_PATH_PREFIX, SAMPLE_AMOUNT_KEY, SHAVAS_INPUT_IMAGES_PATH

    json_Obj = request.get_json()

    json_images = [json_Obj[DATA_0_KEY], json_Obj[DATA_1_KEY]]

    for index, drawing in enumerate(json_images):
        header, encoded = drawing.split(",", 1)
        decoded_data = base64.b64decode(encoded)
        drawing_path = IMAGE_PATH_PREFIX + 'canvasImage_' + str(index) + '.png'

        saveImagesToPath(decoded_data, drawing_path)

        image_list.append(appendPreparedImage(drawing_path))

    createThreadForSamplesCreation(json_Obj[SAMPLE_AMOUNT_KEY], image_list)

    return jsonify(
        'Saved Images and generation of data has started, please wait.'), 200


# checks if a neural network model already exists
@app.route('/if_neural_network', methods=['GET'])
def if_neural_network():
    path = './' + getModelName()
    if (os.path.isfile(path)):
        return jsonify(True), 200
    else:
        return jsonify(False), 201


# gets the current samples list as lists in list for json.dump
@app.route('/getSample', methods=['GET'])
def getSample():
    global samples_and_nn_isDone

    for t in getThreadList():
        if not t.isAlive():
            # get results from thtead
            t.handled = True
    my_threads = [t for t in getThreadList() if not t.handled]

    js = {"sample_list": getSamplesListAsJson(), "samples_created": my_threads}
    return Response(json.dumps(js), mimetype='application/json'), 200


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
    app.run(debug=True)