import numpy as np
import random, math, pickle
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, Conv2D, MaxPooling2D
from samples import getSamplesList, getShapeList
from support_Functions import getShapeInfo, getMaxSamplesConst

training_data_list = []
model_name = 'shape_canvas_model.h5'


def createTrainingData_Conv():
    samples_list = getSamplesList()
    shape_list = getShapeList()

    X_new_shape = None

    for index, sample in enumerate(samples_list):
        training_data_list.append([sample, shape_list[index]])
        if (index == 0):
            X_new_shape = getShapeInfo(sample)

    random.shuffle(training_data_list)

    X = []
    y = []

    for features, labels in training_data_list:
        X.append(features)
        y.append(labels)

    X_reshaped = np.array(X).reshape(-1, X_new_shape[0], X_new_shape[1], 1)

    X_reshaped = X_reshaped / 255.0

    pickle_out = open('X.pickle', 'wb')
    pickle.dump(X_reshaped, pickle_out)
    pickle_out.close()

    pickle_out = open('y.pickle', 'wb')
    pickle.dump(y, pickle_out)
    pickle_out.close()

    model = Sequential()

    # creating a convolutional layer with specific parameters
    # '64' - the size of the output
    # '(3,3)' - the convolution window
    # 'input_shape = X.shape[1:]' - returns the shape of the current images; in this case 50, 50, 1
    # where the 50's are the width and height of the images and 1 is the amount of color-channels
    # that they have
    model.add(Conv2D(64, (3, 3), input_shape=X_reshaped.shape[1:]))
    # some kind of activation function
    model.add(Activation('relu'))
    # here after every convolution we pool a 2x2 unit from the image
    # so basically we are downsizing the image from 3x3 -> 2x2
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(64))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    try:
        model.fit(X_reshaped, y, batch_size=32, epochs=3, validation_split=0.2)
        model.save(model_name)
        return True
    except (RuntimeError, ValueError) as e:
        print('===> Error occured - neural_network.py', e)
        return False

    # new_model = tf.keras.models.load_model('dog_cat_model.h5')


def getModelName():
    return model_name