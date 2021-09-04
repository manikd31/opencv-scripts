import keras
from keras.datasets import mnist
from keras.layers import Conv2D
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Flatten
from keras.layers import MaxPooling2D
from keras.models import load_model
from keras.models import Model
from keras.models import Sequential
from keras.applications.vgg16 import VGG16
import numpy as np
import os
from PIL import Image
from PIL import ImageOps
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelBinarizer


def main():
    num_classes = 10
    model_path = r"C:/Users/Manik/Desktop/my_aug_model"

    _train = not os.path.isdir(model_path)

    if _train:

        # the data, split between train and test sets
        (x_train, y_train), (x_test, y_test) = mnist.load_data()

        # Scale images to the [0, 1] range
        ltr = len(x_train)
        for i in range(ltr):
            if i % 1000 == 0:
                print(f"Processed {i} / {ltr}")
            im = x_train[i]
            im = np.array(ImageOps.invert(Image.fromarray(np.uint8(im))))
            im = np.reshape(im, (1, 28, 28))
            x_train = np.vstack((x_train, im))
            y_train = np.append(y_train, y_train[i])

        lts = len(x_test)
        for i in range(lts):
            if i % 1000 == 0:
                print(f"Processed {i} / {lts}")
            im = x_test[i]
            im = np.array(ImageOps.invert(Image.fromarray(np.uint8(im))))
            im = np.reshape(im, (1, 28, 28))
            x_test = np.vstack((x_test, im))
            y_test = np.append(y_test, y_test[i])

        x_train = x_train.astype("float32") / 255
        x_test = x_test.astype("float32") / 255
        # Make sure images have shape (28, 28, 1)
        x_train = np.expand_dims(x_train, -1)
        x_test = np.expand_dims(x_test, -1)

        print("x_train shape:", x_train.shape)
        print("x_test shape:", x_test.shape)
        print(x_train.shape[0], "train samples")
        print(x_test.shape[0], "test samples")

        # convert class vectors to binary class matrices
        label_bin = LabelBinarizer()
        y_train = label_bin.fit_transform(y_train)
        y_test = label_bin.transform(y_test)

        model = Sequential(
            [
                Conv2D(32, (3, 3), activation="relu", input_shape=(28, 28, 1)),
                MaxPooling2D((2, 2)),
                Conv2D(64, (3, 3), activation="relu"),
                MaxPooling2D((2, 2)),
                Flatten(),
                Dropout(0.5),
                Dense(256, activation="relu"),
                Dropout(0.5),
                Dense(num_classes, activation="softmax"),
            ]
        )

        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        model.fit(x_train, y_train, batch_size=256, epochs=20, validation_data=(x_test, y_test))
        model.save(model_path)

        y_pred = np.argmax(model.predict(x_test), axis=1)
        y_true = label_bin.inverse_transform(y_test)

        print(f"    [INFO]\tScore = {round(accuracy_score(y_true, y_pred), 4)}")

    # saved_model = load_model(model_path)


if __name__ == "__main__":
    main()
