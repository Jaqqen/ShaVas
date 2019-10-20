from flask import Flask, jsonify, request, Response
from threading import Thread
from tensorflow.keras.utils import normalize
import tensorflow as tf
import numpy as np
import base64, os, time, json, cv2
import support_Functions as supF
from samples import createSamples, getSamplesListForJSON, clearBothDataLists
from neural_network import create_training_data_conv, getModelName

app = Flask(__name__)

# temporarily holds holds both canvas-input data
temp_data_list = []

# holds both images - prepareImageBeforeConversion and convertPixelValues
# also is used when createMultipleSamples
image_list = []

# is used to tell the frontend that all samples have been created and the
# neural network has been build
samples_and_nn_isDone = False

# path prefix for the images
IMAGEPATHPREFIX = '../drawnImages/'

# amount of samples that was passed from the frontend
amount_of_samples_to_create = 0

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
    global amount_of_samples_to_create

    json_Obj = request.get_json()

    temp_data_list.append(json_Obj['data0'])
    temp_data_list.append(json_Obj['data1'])

    amount_of_samples_to_create = json_Obj['sampleAmount']

    for index, data in enumerate(temp_data_list):
        header, encoded = data.split(",", 1)
        decoded_data = base64.b64decode(encoded)
        path = IMAGEPATHPREFIX + 'canvasImage_' + str(index) + '.png'
        with open(path, 'wb') as f:
            f.write(decoded_data)
        # appending the images with converted drawing pixels and resized
        image_list.append(
            supF.convertPixelValues(supF.prepareImageBeforeConversion(path)))
    path_of_undefined = IMAGEPATHPREFIX + 'canvasImage_undefined.png'
    image_list.append(
        supF.convertPixelValues(
            supF.prepareImageBeforeConversion(path_of_undefined)))

    Thread(target=createMultipleSamples).start()

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

    sample_list = getSamplesListForJSON()

    js = {"sample_list": sample_list, "samples_created": samples_and_nn_isDone}
    return Response(json.dumps(js), mimetype='application/json'), 200


# identifies the image
@app.route('/identify', methods=['POST'])
def identify():
    data_i = request.get_json()['dataI']
    header, encoded = data_i.split(",", 1)
    decoded_data = base64.b64decode(encoded)
    path = IMAGEPATHPREFIX + 'identifyerImage.png'
    with open(path, 'wb') as f:
        f.write(decoded_data)

    image = supF.prepareImageBeforeConversion(path)
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
    for index, image_name in enumerate(os.listdir(IMAGEPATHPREFIX)):
        if (image_name == 'canvasImage_0.png'):
            path = IMAGEPATHPREFIX + image_name
            image = cv2.imread(path, 0)
            shape_one_image = image.tolist()
        elif (image_name == 'canvasImage_1.png'):
            path = IMAGEPATHPREFIX + image_name
            image = cv2.imread(path, 0)
            shape_two_image = image.tolist()

    sample_list = getSamplesListForJSON()

    js = {
        "shape_one_image": shape_one_image,
        "shape_two_image": shape_two_image,
        "sample_list": sample_list,
    }
    return Response(json.dumps(js), mimetype='application/json'), 200


# creates samples for first and second shape and returns a boolean
# to indicate if all samples have been created
def createMultipleSamples():

    global samples_and_nn_isDone
    global image_list

    clearBothDataLists()

    for index, image in enumerate(image_list):
        for i in range(0, amount_of_samples_to_create):
            print('<------------ :', i, ' -- ', index)
            if (index == 0):
                createSamples(image, 0)
            elif (index == 1):
                createSamples(image, 1)
            else:
                pass
                # createSamples(image, 2)

    samples_and_nn_isDone = create_training_data_conv()
    return samples_and_nn_isDone


if __name__ == '__main__':
    app.run(debug=True)