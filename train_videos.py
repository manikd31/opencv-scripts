"""
Script to train a model on videos by stacking frames.

Usage:
    train_model.py (-h | --help)
"""
from typing import Tuple

import keras.models
from docopt import docopt
from keras.datasets import mnist
from keras.layers import Conv2D
from keras.layers import Conv3D
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Flatten
from keras.layers import MaxPooling2D
from keras.layers import MaxPooling3D
from keras.models import Sequential
from PIL import Image
from PIL import ImageOps
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelBinarizer
import numpy as np
import os
import pandas as pd

# 5-second videos (choose one of these)
# ----> @ 8 fps     =   40 frames
# ----> @ 10 fps    =   50 frames
# ----> @ 12 fps    =   60 frames
NUM_FRAMES = 40
IMAGE_SIZE = 100
INPUT_3D_SHAPE = (IMAGE_SIZE, IMAGE_SIZE, NUM_FRAMES, 3)
INPUT_2D_SHAPE = (IMAGE_SIZE, IMAGE_SIZE, 3)
NUM_CLASSES = 8


def get_3d_model(input_shape: Tuple[int, int, int, int],
                 num_classes: int) -> keras.models.Sequential:
    """Method to get the model with the specified input and output shapes."""
    model = Sequential(
        [
            # conv block 1
            Conv3D(64, (3, 3, 3), activation="relu", input_shape=input_shape),
            MaxPooling3D((2, 2, 2)),
            # conv block 2
            Conv3D(128, (3, 3, 3), activation="relu"),
            MaxPooling3D((2, 2, 2)),
            # conv block 3
            Conv3D(256, (3, 3, 3), activation="relu"),
            # Conv3D(256, (3, 3, 3), activation="relu"),
            MaxPooling3D((2, 2, 2)),
            # conv block 4
            # Conv3D(512, (3, 3, 3), activation="relu"),
            # Conv3D(256, (3, 3, 3), activation="relu"),
            # MaxPooling3D((2, 2, 2)),
            # # conv block 5
            # Conv3D(256, (3, 3, 3), activation="relu"),
            # Conv3D(256, (3, 3, 3), activation="relu"),
            # MaxPooling3D((2, 2, 2)),
            # flatten
            Flatten(),
            Dropout(0.5),
            # fc 1
            Dense(1024, activation="relu"),
            Dropout(0.5),
            # output
            Dense(num_classes, activation="softmax"),
        ]
    )

    return model


def get_2d_model(input_shape: Tuple[int, int, int],
                 num_classes: int) -> keras.models.Sequential:
    """Method to get the model with the specified input and output shapes."""
    model = Sequential(
        [
            # conv block 1
            Conv2D(16, (3, 3), activation="relu", input_shape=input_shape),
            MaxPooling2D((2, 2)),
            # conv block 2
            Conv2D(32, (3, 3), activation="relu"),
            MaxPooling2D((2, 2)),
            # conv block 3
            Conv2D(64, (3, 3), activation="relu"),
            Conv2D(64, (3, 3), activation="relu"),
            MaxPooling2D((2, 2)),
            # conv block 4
            # Conv2D(256, (3, 3), activation="relu"),
            # Conv2D(256, (3, 3), activation="relu"),
            # MaxPooling2D((2, 2)),
            # # conv block 5
            # Conv2D(256, (3, 3), activation="relu"),
            # Conv2D(256, (3, 3), activation="relu"),
            # MaxPooling2D((2, 2)),
            # flatten
            Flatten(),
            Dropout(0.5),
            # fc 1
            Dense(1024, activation="relu"),
            Dropout(0.5),
            # output
            Dense(num_classes, activation="softmax"),
        ]
    )

    return model


def main():
    """Main body of the script."""
    # Data shape = (Samples, Frames, Width, Height, Channels)
    # 3D Input shape = (Frames, Width, Height, Channels)
    # 2D Input shape = (Width, Height, Channels)
    test_3d_input = np.random.random((500, IMAGE_SIZE, IMAGE_SIZE, NUM_FRAMES, 3))
    test_2d_input = np.random.random((500, IMAGE_SIZE, IMAGE_SIZE, 3))
    _classes = np.random.randint(0, 8, (500,))
    lbin = LabelBinarizer()
    test_classes = lbin.fit_transform(_classes)

    print(test_3d_input.shape)
    print(test_2d_input.shape)
    print(test_classes.shape)

    model = get_3d_model(INPUT_3D_SHAPE, NUM_CLASSES)

    print()
    print(model.summary())


# def save_videos(path_in, path_out, _id):
#     ret_array = []
#     start = time.time()
#     cap = cv2.VideoCapture(path_in)
#     num_frames = cap.get(PROP_ID_FRAME_COUNT)
#
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         frame = Image.fromarray(frame)
#         frame = frame.resize((216, 216))
#         frame = np.reshape(frame, (1, 216, 216, 3))
#         frame = np.array(frame)
#
#         if len(ret_array) == 0:
#             ret_array = frame
#         else:
#             ret_array = np.vstack((ret_array, frame))
#
#     ret_array = np.array(ret_array)
#     np.save(path_out, ret_array)
#
#     cap.release()
#
#     stop = time.time()
#     elapsed = round((stop - start))
#     print(f"Time taken to process {num_frames} frames : {elapsed} seconds, final shape = {ret_array.shape}")


if __name__ == "__main__":
    main()
