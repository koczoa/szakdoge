import math

import tensorflow as tf

import keras
import numpy as np
import os
import random

from keras import Sequential, Input
from keras.src.layers import LSTM, Dropout, Dense

mapSize = 32
mapDepth = 8
train_data_dir = "train_data_4"


gpus = tf.config.list_physical_devices("GPU")
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
        tf.config.set_logical_device_configuration(
            gpus[0],
            [tf.config.LogicalDeviceConfiguration(memory_limit=6144)])
        logical_gpus = tf.config.list_logical_devices("GPU")
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        print(e)


def check_data(retreats, scouts, conquers, attacks):
    choices = {"retreats": retreats,
               "scouts": scouts,
               "conquers": conquers,
               "attacks": attacks}

    total_data = 0
    lengths = []
    for choice in choices:
        total_data += len(choices[choice])
        lengths.append(len(choices[choice]))
    return lengths


def load_data(retreats, scouts, conquers, attacks):
    all_files = os.listdir(train_data_dir)
    random.shuffle(all_files)

    for file in all_files:
        full_path = os.path.join(train_data_dir, file)
        data = np.load(full_path)
        data = list(data)
        for d in data:
            choice = np.argmax(d[0:4])
            if choice == 0:
                retreats.append([d[0:4], d[4:]])
            elif choice == 1:
                scouts.append([d[0:4], d[4:]])
            elif choice == 2:
                conquers.append([d[0:4], d[4:]])
            elif choice == 3:
                attacks.append([d[0:4], d[4:]])
    return retreats, scouts, conquers, attacks


def shuffle_data(retreats, scouts, conquers, attacks):
    random.shuffle(retreats)
    random.shuffle(scouts)
    random.shuffle(conquers)
    random.shuffle(attacks)
    return retreats, scouts, conquers, attacks


def prepare_autoEncoder():
    retreats, scouts, conquers, attacks = load_data([], [], [], [])
    # retreats, scouts, conquers, attacks = shuffle_data(retreats, scouts, conquers, attacks)
    train_data = retreats + scouts + conquers + attacks
    print(f"train_data len: {len(train_data)}")
    # random.shuffle(train_data)
    test_size = math.floor(len(train_data) * 0.1)

    x_train = np.array([i[1] for i in train_data[:-test_size]]).reshape(-1, mapSize, mapSize, mapDepth)
    y_train = np.array([i[0] for i in train_data[:-test_size]])

    x_test = np.array([i[1] for i in train_data[-test_size:]]).reshape(-1, mapSize, mapSize, mapDepth)
    y_test = np.array([i[0] for i in train_data[-test_size:]])

    return x_train, y_train, x_test, y_test


def prepare_lstm(encoder, x_train, x_test):
    encoded_trains = []
    encoded_tests = []
    for train in x_train:
        encoded_trains.append(encoder.predict(train.reshape(-1, mapSize, mapSize, mapDepth))[0])
    for test in x_test:
        encoded_tests.append(encoder.predict(test.reshape(-1, mapSize, mapSize, mapDepth))[0])

    return encoded_trains, encoded_tests


def train_autoEncoder(x_train):
    encoder_input = keras.Input(shape=(mapSize, mapSize, mapDepth))
    x = keras.layers.Flatten()(encoder_input)
    x = keras.layers.Dense(8192, activation="leaky_relu")(x)
    x = keras.layers.Dense(2048, activation="leaky_relu")(x)
    x = keras.layers.Dense(512, activation="leaky_relu")(x)
    x = keras.layers.Dense(256, activation="leaky_relu")(x)
    encoder_output = keras.layers.Dense(256, activation="sigmoid")(x)

    encoder = keras.Model(encoder_input, encoder_output, name="encoder")

    decoder_input = keras.layers.Dense(256, activation="leaky_relu")(encoder_output)
    x = keras.layers.Dense(256, activation="leaky_relu")(decoder_input)
    x = keras.layers.Dense(512, activation="leaky_relu")(x)
    x = keras.layers.Dense(2048, activation="leaky_relu")(x)
    x = keras.layers.Dense(8192, activation="sigmoid")(x)
    decoder_output = keras.layers.Reshape((mapSize, mapSize, mapDepth))(x)

    opt = tf.keras.optimizers.Adam(learning_rate=0.001, decay=1e-6)

    autoencoder = keras.Model(encoder_input, decoder_output, name="autoencoder")

    autoencoder.summary()
    autoencoder.compile(opt, loss="mse")
    autoencoder.fit(x_train, x_train, epochs=10, batch_size=8, validation_split=0.20)
    autoencoder.save("models/AE.keras")
    encoder.save("models/E.keras")
    return encoder


def train_LSTM(x_train, y_train, x_test, y_test):
    x_train = x_train.reshape(-1, 256, 1)
    x_test = x_test.reshape(-1, 256, 1)

    lstm = Sequential()
    lstm.add(Input(shape=(x_train.shape[1:])))

    lstm.add(LSTM(units=256, return_sequences=True))
    lstm.add(Dropout(0.2))
    lstm.add(LSTM(units=256, return_sequences=True))
    lstm.add(Dropout(0.2))
    lstm.add(LSTM(units=256))
    lstm.add(Dropout(0.2))

    lstm.add(Dense(units=4, activation="softmax"))

    lstm.summary()
    lstm.compile(loss="categorical_crossentropy", optimizer="rmsprop", metrics=["accuracy"])
    lstm.fit(x_train, y_train, epochs=1, validation_data=(x_test, y_test))
    lstm.save("models/LSTM.keras")


from_save = False


def main():
    x_train, y_train, x_test, y_test = prepare_autoEncoder()
    if from_save:
        e_x_train = np.load("LSTM/e_x_train.npy")
        e_x_test = np.load("LSTM/e_x_test.npy")
        y_train = np.load("AE/y_train.npy")
        y_test = np.load("AE/y_test.npy")
    else:
        np.save("AE/x_train.npy", x_train)
        np.save("AE/y_train.npy", y_train)
        np.save("AE/x_test.npy", x_test)
        np.save("AE/y_test.npy", y_test)
        encoder = train_autoEncoder(x_train)
        e_x_train, e_x_test = prepare_lstm(encoder, x_train, x_test)
        np.save("LSTM/e_x_train.npy", e_x_train)
        np.save("LSTM/e_x_test.npy", e_x_test)

    train_LSTM(e_x_train, y_train, e_x_test, y_test)


if __name__ == "__main__":
    main()
