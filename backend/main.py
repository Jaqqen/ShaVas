from flask import Flask, jsonify, request, Response
from threading import Thread
import tensorflow as tf
import numpy as np
import base64, os, time, json
import support_Functions as supF
from samples import createSamples, getDatasetAsTuple, getSamplesList
from neural_network import createTrainingData_Conv, getModelName

app = Flask(__name__)

data_list = []
shape_list = []

image_list = []

random_sample_value = 0
created_samples = False
print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
print('!!!!!!!!!!!!!START MAIN!!!!!!!!!!!!!')
print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


@app.route('/clear_datalist', methods=['GET'])
def clear_datalist():
    global random_sample_value
    print("============================ \n")
    print("CLEAR_DATALIST \n")
    print("============================ \n")
    data_list.clear()
    shape_list.clear()
    image_list.clear()
    random_sample_value = 0

    response_str = ('>>> Cleared datalist amount: ' + str(len(data_list)),
                    '>>> Cleared shapeList amount: ' + str(len(shape_list)),
                    '>>> Cleared image_list:  ' + str(len(image_list)))
    return jsonify(response_str), 200


@app.route('/send_canvas', methods=['POST'])
def send_canvas():
    json_Obj = request.get_json();

    data_list.append(json_Obj['data0'])
    data_list.append(json_Obj['data1'])
    shape_list.append(json_Obj['shape0'])
    shape_list.append(json_Obj['shape1'])
    print("============================ \n")
    print("SEND_CANVAS \n")
    for index, data in enumerate(data_list):
        header, encoded = data.split(",", 1)
        decoded_data = base64.b64decode(encoded)
        path = '../drawnImages/canvasImage_' + str(index) + '.png'
        with open(path, 'wb') as f:
            f.write(decoded_data)
        image_list.append(
            supF.convertPixelValues(supF.prepareImageBeforeConversion(path)))
    print("============================ \n")
    print("============================ \n")
    print("!!!!!!!!!GENERATE!!!!!!!!")
    Thread(target=createMultipleSamples).start()
    print("============================ \n")


    return jsonify('Saved Images and generation of data has started, please wait.'), 200


@app.route('/if_neural_network', methods=['GET'])
def if_neural_network():
    path = './' + getModelName()
    if (os.path.isfile(path)):
        return jsonify(True), 200
    else:
        return jsonify(False), 201


@app.route('/generate', methods=['GET'])
def generate():

    print('========================= \n')
    print('!!!!!!!!!GENERATE!!!!!!!!')
    print('========================= \n')
    Thread(target=createMultipleSamples).start()

    return jsonify('Samples are being created'), 200


@app.route('/getSample', methods=['GET'])
def getSample():

    sample, samples_created = buildJsonForGetSample()

    js = [{"sample": sample.tolist(), "samples_created": samples_created}]

    return Response(json.dumps(js), mimetype='application/json'), 200


@app.route('/identify', methods=['POST'])
def identify():
    data_i = request.get_json()['dataI']
    header, encoded = data_i.split(",", 1)
    decoded_data = base64.b64decode(encoded)
    path = './drawnImages/identifyerImage.png'
    with open(path, 'wb') as f:
        f.write(decoded_data)
    image = supF.prepareImageBeforeConversion(path)
    my_model = tf.keras.models.load_model('./shape_canvas_model.h5')
    image_reshaped = np.array(image).reshape(-1, image.shape[1],
                                             image.shape[0], 1)
    predictions = my_model.predict(image_reshaped)
    print(predictions)

    return Response(json.dumps(predictions.tolist()),
                    mimetype='application/json'), 200


def createMultipleSamples():

    global created_samples
    global image_list

    for index, image in enumerate(image_list):
        for i in range(0, supF.getMaxSamplesConst()):
            if (index == 0):
                print('==> SHAPE 0 ---- image_index ' + str(index) +
                      ' ---- i; ' + str(i) + '<==')
                createSamples(image, 0.0)
            else:
                print('==> SHAPE 1 ---- image_index ' + str(index) +
                      ' ---- i; ' + str(i) + '<==')
                createSamples(image, 1.0)

            if (index == 1 and i == supF.getMaxSamplesConst() - 1):
                created_samples = True

    return created_samples


def buildJsonForGetSample():
    global random_sample_value
    samples_list = getSamplesList()
    random_sample_value += 60
    print('========================= \n')
    print('INDEX', random_sample_value)
    print('CREATED SAMPLES', created_samples)
    print('========================= \n')

    return (samples_list[random_sample_value], created_samples)


if __name__ == '__main__':
    app.run(debug=True)