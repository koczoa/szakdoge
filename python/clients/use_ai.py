import keras
import matplotlib.pyplot as plt
from autoEncoder import mapSize, mapDepth, prepare


def use(x_test, y_test):
    model = keras.saving.load_model("models/AE.keras")
    name = "yiumyum"
    encoder = keras.saving.load_model("models/E.keras")
    example = encoder.predict([x_test[0].reshape(-1, mapSize, mapSize, 8)])
    ae_out = model.predict([x_test[0].reshape(-1, mapSize, mapSize, 8)])
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
    test = model.predict([x_test[0].reshape(-1, mapSize, mapSize, mapDepth)])[0]
    fig = plt.figure(figsize=plt.figaspect(0.5))
    ax = fig.add_subplot(1, 2, 2, projection='3d')
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
    img = ax.scatter(x, y, z, c=c, cmap=plt.viridis())
    ax.set_title("decoded")
    fig.colorbar(img)




    ax = fig.add_subplot(1, 2, 1, projection='3d')
    orig = x_test[0].reshape(-1, mapSize, mapSize, mapDepth)[0]
    x = []
    y = []
    z = []
    c = []
    for i in range(0, 32):
        for j in range(0, 32):
            for k in range(0, 8):
                if orig[i][j][k] != 0:
                    x.append(i)
                    y.append(j)
                    z.append(k)
                    c.append(test[i][j][k])

    img = ax.scatter(x, y, z, c=c, cmap=plt.viridis())
    fig.colorbar(img)
    ax.set_title("original")

    plt.show()

def main():
    x_train, y_train, x_test, y_test = prepare()
    use(x_test, y_test)


if __name__ == "__main__":
    main()
