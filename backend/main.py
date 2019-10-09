from flask import Flask, jsonify, request, Response
from threading import Thread
import tensorflow as tf
import numpy as np
import base64, os, time, json
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

print('!!!!!!!!!!!!!!!!!!!!!!!!!!')
print('!!!!!!!!START MAIN!!!!!!!!')
print('!!!!!!!!!!!!!!!!!!!!!!!!!!')


# Clears Data when starting application or refreshing
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
# async action: creates multiple different samples
@app.route('/send_canvas', methods=['POST'])
def send_canvas():
    json_Obj = request.get_json()

    temp_data_list.append(json_Obj['data0'])
    temp_data_list.append(json_Obj['data1'])

    for index, data in enumerate(temp_data_list):
        header, encoded = data.split(",", 1)
        decoded_data = base64.b64decode(encoded)
        path = IMAGEPATHPREFIX + 'canvasImage_' + str(index) + '.png'
        with open(path, 'wb') as f:
            f.write(decoded_data)
        # appending the images with converted drawing pixels and resized
        image_list.append(
            supF.convertPixelValues(supF.prepareImageBeforeConversion(path)))

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
    my_model = tf.keras.models.load_model('./shape_canvas_model.h5')
    image_reshaped = np.array(image).reshape(-1, image.shape[0],
                                             image.shape[1], 1)
    predictions = my_model.predict(image_reshaped)

    return Response(json.dumps(predictions.tolist()),
                    mimetype='application/json'), 200


# creates samples for first and second shape and returns a boolean
# to indicate if all samples have been created
def createMultipleSamples():

    global samples_and_nn_isDone
    global image_list

    clearBothDataLists()

    for index, image in enumerate(image_list):
        for i in range(0, supF.getMaxSamplesConst()):
            print('<------------ :', i)
            if (index == 0):
                createSamples(image, 0.0)
            else:
                createSamples(image, 1.0)

    samples_and_nn_isDone = create_training_data_conv()
    return samples_and_nn_isDone


if __name__ == '__main__':
    app.run(debug=True)