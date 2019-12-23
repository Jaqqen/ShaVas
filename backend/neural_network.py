import random
import pickle
import numpy as np
from tensorflow.keras.utils import normalize
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, Conv2D, MaxPooling2D
from samples import getSamplesList, getShapeList
from support_Functions import getShapeInfo

training_data_list = []
model_name = 'shape_canvas_model.h5'


def create_training_data_conv():
    samples_list = getSamplesList()
    shape_list = getShapeList()

    pickle_out = open('X.pickle', 'wb')
    pickle.dump(samples_list, pickle_out)
    pickle_out.close()

    pickle_out = open('y.pickle', 'wb')
    pickle.dump(shape_list, pickle_out)
    pickle_out.close()

    # X_new_shape = None

    training_data_list.clear()

    for index, sample in enumerate(samples_list):
        training_data_list.append([sample, shape_list[index]])
        # if (index == 0):
        #     X_new_shape = getShapeInfo(sample)

    random.shuffle(training_data_list)

    X = []
    y = []

    for features, labels in training_data_list:
        X.append(features)
        y.append(labels)

    X = np.asarray(X)
    y = np.asarray(y)

    # ! needs to be fixed when work on backend starts
    X_reshaped = normalize(X, axis=1)
    # X_reshaped = np.asarray(X) / 255.0
    # X_reshaped = np.array(X).reshape(-1, X_new_shape[1], X_new_shape[0], 1)

    model = Sequential()

    # model.add(Conv2D(32, (5, 5), input_shape=X_reshaped.shape[1:]))
    # model.add(Activation('relu'))
    # model.add(MaxPooling2D(pool_size=(2, 2)))

    # model.add(Conv2D(64, (4, 4)))
    # model.add(Activation('relu'))
    # model.add(MaxPooling2D(pool_size=(2, 2)))
    # model.add(Dropout(rate=0.3))

    # model.add(Conv2D(128, (3, 3)))
    # model.add(Activation('relu'))
    # model.add(MaxPooling2D(pool_size=(2, 2)))
    # model.add(Dropout(rate=0.2))

    # model.add(Flatten())
    # model.add(Dense(256))
    # model.add(Activation('relu'))

    # model.add(Dense(3))
    # model.add(Activation('softmax'))

    model.add(Flatten(input_shape=(75, 100)))
    model.add(Dense(300))
    model.add(Activation('relu'))
    model.add(Dense(100))
    model.add(Activation('relu'))
    model.add(Dense(2))
    model.add(Activation('softmax'))

    model.compile(loss='sparse_categorical_crossentropy',
                  optimizer='Adam',
                  metrics=['accuracy'])

    try:
        model.fit(X_reshaped, y, epochs=6, validation_split=0.05)
        model.save(model_name)
        return True
    except (RuntimeError, ValueError) as e:
        print('===> Error occured - neural_network.py', e)
        return False


def getModelName():
    return model_name
