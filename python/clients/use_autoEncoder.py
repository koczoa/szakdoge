import keras
import matplotlib.pyplot as plt
from autoEncoder import mapSize, mapDepth, prepare


def use(x_test, y_test):
    model = keras.saving.load_model("models/AE.keras")
    print(f"shape is :{x_test[0].shape}")
    test = model.predict([x_test[0].reshape(-1, mapSize, mapSize, mapDepth)])[0]
    fig = plt.figure(figsize=plt.figaspect(0.5))
    ax = fig.add_subplot(1, 2, 3, projection='3d')
    x = []
    y = []
    z = []
    c = []
    for i in range(0, mapSize):
        for j in range(0, mapSize):
            for k in range(0, mapDepth):
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
    for i in range(0, mapSize):
        for j in range(0, mapSize):
            for k in range(0, mapDepth):
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
