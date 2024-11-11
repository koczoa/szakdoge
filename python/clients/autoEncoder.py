import tensorflow as tf
import matplotlib.pyplot as plt
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
            [tf.config.LogicalDeviceConfiguration(memory_limit=3072)])
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
            print(f"d0: {d[0]}")
            print(f"lend1: {len(d[1:])}")
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
    x = keras.layers.Dense(4096, activation="relu")(x)
    x = keras.layers.Dense(2048, activation="relu")(x)
    x = keras.layers.Dense(1024, activation="relu")(x)
    x = keras.layers.Dense(512, activation="relu")(x)
    x = keras.layers.Dense(256, activation="relu")(x)
    encoder_output = keras.layers.Dense(256, activation="relu")(x)

    encoder = keras.Model(encoder_input, encoder_output, name='encoder')

    decoder_input = keras.layers.Dense(256, activation="relu")(encoder_output)
    x = keras.layers.Dense(256, activation="relu")(decoder_input)
    x = keras.layers.Dense(512, activation="relu")(x)
    x = keras.layers.Dense(1024, activation="relu")(x)
    x = keras.layers.Dense(2048, activation="relu")(x)
    x = keras.layers.Dense(4096, activation="relu")(x)
    x = keras.layers.Dense(8192, activation="relu")(x)
    decoder_output = keras.layers.Reshape((mapSize, mapSize, mapDepth))(x)

    opt = tf.keras.optimizers.Adam(learning_rate=0.001, decay=1e-6)

    autoencoder = keras.Model(encoder_input, decoder_output, name='autoencoder')

    autoencoder.summary()
    autoencoder.compile(opt, loss='mse')
    history = autoencoder.fit(x_train, x_train, epochs=10, batch_size=16, validation_split=0.10)
    autoencoder.save("models/AE.keras")
    encoder.save("models/E.keras")


def use(x_test, y_test):
    model = keras.saving.load_model("models/AE.keras")
    name = "yiumyum"
    encoder = keras.saving.load_model("models/E.keras")
    example = encoder.predict([x_test[0].reshape(-1, mapSize, mapSize, 8)])
    ae_out = model.predict([x_test[0].reshape(-1, mapSize, mapSize, 8)])
    print(example[0].shape)
    # graph, (original, encoded, decoded) = plt.subplots(1, 3)
    # original.imshow(x_test[0], cmap="gray", interpolation="none")
    # original.set_title("AE/original")
    # encoded.imshow(example[0].reshape((8, 8)), cmap="gray", interpolation="none")
    # encoded.set_title("E/encoded")
    # decoded.imshow(ae_out[0], cmap="gray", interpolation="none")
    # decoded.set_title("AE/decoded")
    # graph.tight_layout()
    # plt.suptitle(name)
    # plt.savefig(f"models/{name}.png")

    # test = x_test[0]
    test = model.predict([x_test[0].reshape(-1, mapSize, mapSize, 8)])[0]
    print(test.shape)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x = np.linspace(0, 31, 32).astype(int)
    y = np.linspace(0, 31, 32).astype(int)
    z = np.linspace(0, 7, 8).astype(int)
    c = test

    x = []
    y = []
    z = []
    c = []
    for i in range(0, 32):
        for j in range(0, 32):
            for k in range(0, 8):
                if test[i][j][k] != 0:
                    x.append(i)
                    y.append(j)
                    z.append(k)
                    c.append(test[i][j][k])

    img = ax.scatter(x, y, z, c=c, cmap=plt.hot())
    fig.colorbar(img)
    plt.show()


def main():
    x_train, y_train, x_test, y_test = prepare()
    train(x_train, y_train, x_test, y_test)
    # use(x_test, y_test)


if __name__ == "__main__":
    main()
