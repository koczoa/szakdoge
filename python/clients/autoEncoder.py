import tensorflow as tf

import keras
import numpy as np
import os
import random

mapSize = 32
mapDepth = 8
train_data_dir = "train_data_3"


gpus = tf.config.list_physical_devices("GPU")
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
        tf.config.set_logical_device_configuration(
            gpus[0],
            [tf.config.LogicalDeviceConfiguration(memory_limit=4096)])
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
            # print(f"d0: {d[0]}")
            # print(f"lend1: {len(d[1:])}")
            choice = d[0]
            if choice == 0:
                retreats.append([d[0], d[1:]])
            elif choice == 1:
                scouts.append([d[0], d[1:]])
            elif choice == 2:
                conquers.append([d[0], d[1:]])
            elif choice == 3:
                attacks.append([d[0], d[1:]])
    return retreats, scouts, conquers, attacks


def shuffle_data(retreats, scouts, conquers, attacks):
    random.shuffle(retreats)
    random.shuffle(scouts)
    random.shuffle(conquers)
    random.shuffle(attacks)
    return retreats, scouts, conquers, attacks


def prepare():
    retreats, scouts, conquers, attacks = load_data([], [], [], [])
    retreats, scouts, conquers, attacks = shuffle_data(retreats, scouts, conquers, attacks)
    train_data = retreats + scouts + conquers + attacks
    print(f"train_data len: {len(train_data)}")
    random.shuffle(train_data)
    test_size = 1000
    x_train = np.array([i[1] for i in train_data[:-test_size]]).reshape(-1, mapSize, mapSize, mapDepth)
    y_train = np.array([i[0] for i in train_data[:-test_size]])

    x_test = np.array([i[1] for i in train_data[-test_size:]]).reshape(-1, mapSize, mapSize, mapDepth)
    y_test = np.array([i[0] for i in train_data[-test_size:]])

    return x_train, y_train, x_test, y_test


def train(x_train, y_train, x_test, y_test):
    encoder_input = keras.Input(shape=(mapSize, mapSize, mapDepth), name='img')
    x = keras.layers.Flatten()(encoder_input)
    x = keras.layers.Dense(8192, activation="relu")(x)
    # x = keras.layers.Dense(4096, activation="relu")(x)
    x = keras.layers.Dense(2048, activation="relu")(x)
    # x = keras.layers.Dense(1024, activation="relu")(x)
    x = keras.layers.Dense(512, activation="relu")(x)
    x = keras.layers.Dense(256, activation="relu")(x)
    encoder_output = keras.layers.Dense(256, activation="relu")(x)

    encoder = keras.Model(encoder_input, encoder_output, name='encoder')

    decoder_input = keras.layers.Dense(256, activation="relu")(encoder_output)
    x = keras.layers.Dense(256, activation="relu")(decoder_input)
    x = keras.layers.Dense(512, activation="relu")(x)
    # x = keras.layers.Dense(1024, activation="relu")(x)
    x = keras.layers.Dense(2048, activation="relu")(x)
    # x = keras.layers.Dense(4096, activation="relu")(x)
    x = keras.layers.Dense(8192, activation="relu")(x)
    decoder_output = keras.layers.Reshape((mapSize, mapSize, mapDepth))(x)

    opt = tf.keras.optimizers.Adam(learning_rate=0.001, decay=1e-6)

    autoencoder = keras.Model(encoder_input, decoder_output, name='autoencoder')

    autoencoder.summary()
    autoencoder.compile(opt, loss='mse')
    history = autoencoder.fit(x_train, x_train, epochs=20, batch_size=8, validation_split=0.20)
    autoencoder.save("models/AE.keras")
    encoder.save("models/E.keras")


def main():
    x_train, y_train, x_test, y_test = prepare()
    train(x_train, y_train, x_test, y_test)
    

if __name__ == "__main__":
    main()
