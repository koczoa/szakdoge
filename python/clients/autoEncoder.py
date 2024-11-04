import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt
import random
import os

# y_train, x_train =
#
# plt.imshow(x_train[0], cmap="gray")


import keras  # Keras 2.1.2 and TF-GPU 1.9.0
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.callbacks import TensorBoard
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

train_data_dir = "train_data"


def check_data():
    choices = {"retreats": retreats,
               "scouts": scouts,
               "conquers": conquers,
               "attacks": attacks}

    total_data = 0

    lengths = []
    for choice in choices:
        print(f"Length of {choice} is: {len(choices[choice])}")
        total_data += len(choices[choice])
        lengths.append(len(choices[choice]))

    print(f"Total data length now is:{total_data}")
    return lengths


hm_epochs = 1

for i in range(hm_epochs):
    current = 0
    increment = 200
    not_maximum = True
    all_files = os.listdir(train_data_dir)
    maximum = len(all_files)
    random.shuffle(all_files)

    while not_maximum:
        print("WORKING ON {}:{}".format(current, current+increment))
        retreats = []
        scouts = []
        conquers = []
        attacks = []

        for file in all_files[current:current+increment]:
            full_path = os.path.join(train_data_dir, file)
            data = np.load(full_path)
            data = list(data)
            for d in data:
                choice = d[0]
                if choice == 0:
                    retreats.append([d[0], d[1:]])
                elif choice == 1:
                    scouts.append([d[0], d[1:]])
                elif choice == 2:
                    conquers.append([d[0], d[1:]])
                elif choice == 3:
                    attacks.append([d[0], d[1:]])

        lengths = check_data()

        lowest_data = min(lengths)

        random.shuffle(retreats)
        random.shuffle(scouts)
        random.shuffle(conquers)
        random.shuffle(attacks)
        #
        # retreats = retreats[:lowest_data]
        # scouts = scouts[:lowest_data]
        # conquers = conquers[:lowest_data]
        # attacks = attacks[:lowest_data]
        #
        # check_data()

        train_data = retreats + scouts + conquers + attacks
        random.shuffle(train_data)
        test_size = 100
        batch_size = 128

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
        current += increment
        if current > maximum:
            not_maximum = False
# print(x_train[0])
# print(y_train)
# print(" ".join(map(str, y_train)))
plt.imshow(x_train[0], cmap="gray")
plt.show()
