import tensorflow as tf
import matplotlib.pyplot as plt
import keras
import numpy as np
import os
import random


# model = Sequential()
#
# model.add(Conv2D(32, (3, 3), padding='same', input_shape=(176, 200, 3), activation='relu'))
# model.add(Conv2D(32, (3, 3), activation='relu'))
# model.add(MaxPooling2D(pool_size=(2, 2)))
# model.add(Dropout(0.2))
#
# model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
# model.add(Conv2D(64, (3, 3), activation='relu'))
# model.add(MaxPooling2D(pool_size=(2, 2)))
# model.add(Dropout(0.2))
#
# model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
# model.add(Conv2D(128, (3, 3), activation='relu'))
# model.add(MaxPooling2D(pool_size=(2, 2)))
# model.add(Dropout(0.2))
#
# model.add(Flatten())
# model.add(Dense(512, activation='relu'))
# model.add(Dropout(0.5))
# model.add(Dense(4, activation='softmax'))
#
# learning_rate = 0.0001
# opt = keras.optimizers.Adam(lr=learning_rate, decay=1e-6)
#
# model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
#
# tensorboard = TensorBoard(log_dir="logs/STAGE1")


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
    train_data_dir = "train_data"
    all_files = os.listdir(train_data_dir)
    random.shuffle(all_files)

    for file in all_files:
        full_path = os.path.join(train_data_dir, file)
        data = np.load(full_path)
        data = list(data)
        for d in data:
            choice = d[0]
            if choice == 0:
                retreats.append([d[0], d[1:]/255])
            elif choice == 1:
                scouts.append([d[0], d[1:]/255])
            elif choice == 2:
                conquers.append([d[0], d[1:]/255])
            elif choice == 3:
                attacks.append([d[0], d[1:]/255])
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
    test_size = 100
    x_train = np.array([i[1] for i in train_data[:-test_size]]).reshape(-1, 60, 60, 1)
    y_train = np.array([i[0] for i in train_data[:-test_size]])

    x_test = np.array([i[1] for i in train_data[-test_size:]]).reshape(-1, 60, 60, 1)
    y_test = np.array([i[0] for i in train_data[-test_size:]])

    # model.fit(x_train, y_train,
    #           batch_size=batch_size,
    #           validation_data=(x_test, y_test),
    #           shuffle=True,
    #           verbose=1, callbacks=[tensorboard])
    #
    # model.save("BasicCNN-{}-epochs-{}-LR-STAGE1".format(hm_epochs, learning_rate))
    return x_train, y_train, x_test, y_test


def train(x_train, y_train, x_test, y_test):
    encoder_input = keras.Input(shape=(60, 60, 1), name='img')
    x = keras.layers.Flatten()(encoder_input)
    x = keras.layers.Dense(1024, activation="relu")(x)
    x = keras.layers.Dense(256, activation="relu")(x)
    encoder_output = keras.layers.Dense(64, activation="relu")(x)

    encoder = keras.Model(encoder_input, encoder_output, name='encoder')

    decoder_input = keras.layers.Dense(64, activation="relu")(encoder_output)
    x = keras.layers.Dense(256, activation="relu")(decoder_input)
    x = keras.layers.Dense(1024, activation="relu")(x)
    x = keras.layers.Dense(3600, activation="relu")(x)
    decoder_output = keras.layers.Reshape((60, 60, 1))(x)

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
    example = encoder.predict([x_test[0].reshape(-1, 60, 60, 1)])
    ae_out = model.predict([x_test[0].reshape(-1, 60, 60, 1)])
    print(example[0].shape)
    graph, (original, encoded, decoded) = plt.subplots(1, 3)
    original.imshow(x_test[0], cmap="gray", interpolation="none")
    original.set_title("AE/original")
    encoded.imshow(example[0].reshape((8, 8)), cmap="gray", interpolation="none")
    encoded.set_title("E/encoded")
    decoded.imshow(ae_out[0], cmap="gray", interpolation="none")
    decoded.set_title("AE/decoded")
    graph.tight_layout()
    plt.suptitle(name)
    plt.savefig(f"models/{name}.png")


def main():
    x_train, y_train, x_test, y_test = prepare()
    # train(x_train, y_train, x_test, y_test)
    use(x_test, y_test)


if __name__ == "__main__":
    main()
