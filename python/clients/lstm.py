import tensorflow as tf
import keras
from autoEncoder import mapSize, mapDepth, prepare


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


def train(x_train, y_train, x_test, y_test):
    encoder = keras.saving.load_model("models/E.keras")

    # print(encoder.predict())

    lstm = keras.Sequential()
    lstm.add(keras.layers.LSTM(units=256, return_sequences=True, input_shape=(encoder.predict(x_train.shape))))
    lstm.add(keras.layers.Dropout(0.1))

    lstm.add(keras.layers.LSTM(units=256, return_sequences=True))
    lstm.add(keras.layers.Dropout(0.1))

    lstm.add(keras.layers.LSTM(units=256, return_sequences=True))
    lstm.add(keras.layers.Dropout(0.1))

    lstm.add(keras.layers.LSTM(units=256, return_sequences=True))
    lstm.add(keras.layers.Dropout(0.1))

    lstm.add(keras.layers.LSTM(units=256))
    lstm.add(keras.layers.Dropout(0.1))

    lstm.add(keras.layers.Dense(units=4))

    lstm.compile(optimizer="rmsprop", loss="mse")
    lstm.fit(x_train, y_train, epochs=10, batch_size=8)

    lstm.save("models/LSTM.keras")


def main():
    x_train, y_train, x_test, y_test = prepare()
    train(x_train, y_train, x_test, y_test)



if __name__ == "__main__":
    main()
