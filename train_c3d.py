"""
Training script to train a simple C3D model (3D-ConvNet) on the dataset.

Usage:
    train_c3d.py (-h | --help)
"""

from typing import Tuple
from natsort import natsorted
from natsort import ns
import keras
from keras.layers import Conv3D
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Flatten
from keras.layers import MaxPooling3D
from keras.models import Sequential
from PIL import Image
from sklearn.preprocessing import LabelBinarizer
import numpy as np
import os
import time

NUM_FRAMES = 20
IMAGE_SIZE = 100
BATCH_SIZE = 16
EPOCHS = 100

INPUT_3D_SHAPE = (NUM_FRAMES, IMAGE_SIZE, IMAGE_SIZE, 3)

FRAMES_PATH = r"E:/LakeheadU/Final Project Data/frames_dir"
FRAMES_ARRAY_PATH = r"E:/LakeheadU/Final Project Data/frames_array.npy"
LABELS_ARRAY_PATH = r"E:/LakeheadU/Final Project Data/labels_array.npy"
ACCURACY_PATH = r"E:/LakeheadU/Final Project Data/model_accuracy.npy"
LOSS_PATH = r"E:/LakeheadU/Final Project Data/model_loss.npy"
MODEL_SAVE_PATH = r"E:/LakeheadU/Final Project Data/model_weights/complete_model.h5"


def get_c3d_model(input_shape: Tuple[int, int, int, int],
                  num_classes: int) -> keras.models.Sequential:
    """Method to get the model with the specified input and output shapes."""
    model = Sequential(
        [
            # conv block 1
            Conv3D(32, (3, 3, 3), activation="relu", input_shape=input_shape),
            MaxPooling3D((1, 2, 2)),
            # conv block 2
            Conv3D(64, (3, 3, 3), activation="relu"),
            MaxPooling3D((2, 2, 2)),
            # conv block 3
            Conv3D(128, (3, 3, 3), activation="relu"),
            MaxPooling3D((2, 2, 2)),
            # conv block 4
            Conv3D(128, (3, 3, 3), activation="relu"),
            MaxPooling3D((1, 2, 2)),
            # flatten
            Flatten(),
            Dropout(0.5),
            # fc 1
            Dense(256, activation="relu"),
            Dropout(0.5),
            # output
            Dense(num_classes, activation="softmax"),
        ]
    )

    return model


def time_elapsed(elapsed):
    return str(time.strftime('%H:%M:%S', time.gmtime(elapsed)))


def process_videos_for_training():
    """Process all videos and convert and save to numpy arrays to use in the future."""

    if os.path.isdir(FRAMES_PATH):
        class_names = natsorted(os.listdir(FRAMES_PATH), alg=ns.IC)
    else:
        class_names = ['background',
                       'clap',
                       'peace',
                       'swipe_left',
                       'swipe_right',
                       'thumbs_down',
                       'thumbs_up',
                       'wave']

    # Dictionary to store labels with indices
    int2lab = dict()
    lab2int = dict()
    idx = 0
    for c_name in class_names:
        lab2int[c_name] = idx
        int2lab[idx] = c_name
        idx += 1

    # One-hot encoding of labels
    label_binarizer = LabelBinarizer()
    classes = np.array(list(lab2int.values()))
    classes_onehot = label_binarizer.fit_transform(classes)

    # Start processing the data folder
    total_time = time.time()
    start_time = time.time()
    frames_array = np.array([])
    labels_array = []
    # Iterate through all classes
    for c_name in class_names:
        videos = natsorted(os.listdir(os.path.join(FRAMES_PATH, c_name)), alg=ns.IC)
        print(f"    [INFO]\tProcessing class \"{c_name}\" with {len(videos)} videos")
        # Iterate through all videos in a class
        for _id, video in enumerate(videos):
            video_array = np.array([])
            all_frames = natsorted(os.listdir(os.path.join(FRAMES_PATH, c_name, video)), alg=ns.IC)
            # Gather all frames of each videos as a numpy array
            for frame in all_frames:
                path = os.path.join(FRAMES_PATH, c_name, video, frame)
                frame = np.array(Image.open(path))
                frame = np.expand_dims(frame, axis=0)

                # Concatenate all frames to get a video of shape = [20, 100, 100, 3]
                if len(video_array) == 0:
                    video_array = frame
                else:
                    video_array = np.concatenate((video_array, frame))
                del frame

            # Reshape the final video array to [1, array_shape]
            video_array = np.expand_dims(video_array, axis=0)

            if len(frames_array) == 0:
                frames_array = video_array
            else:
                frames_array = np.concatenate((frames_array, video_array))

            labels_array.append(classes_onehot[lab2int.get(c_name)])

            del video_array

        print(f"    [INFO]\t--- Time elapsed = {time_elapsed(time.time() - start_time)} ---\n")
        start_time = time.time()

    labels_array = np.array(labels_array)

    np.save(FRAMES_ARRAY_PATH, frames_array)
    np.save(LABELS_ARRAY_PATH, labels_array)

    print(f"    [INFO]\t--- Total Time elapsed = {time_elapsed(time.time() - total_time)} ---\n")
    print("\n    [INFO]\tDone!\n")


def main():
    """Main body."""

    if not os.path.isfile(FRAMES_ARRAY_PATH) or os.path.isfile(LABELS_ARRAY_PATH):
        process_videos_for_training()

    # Get the frames and labels arrays saved after processing the videos
    x_train = np.load(FRAMES_ARRAY_PATH)
    y_train = np.load(LABELS_ARRAY_PATH)

    # Create the model with the given input shape and output classes
    model = get_c3d_model(x_train.shape[1:], y_train.shape[1])
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['acc'])
    print()
    print(model.summary())
    print()

    # Train the model
    print(f"    [INFO]\t{'=' * 50}")
    print(f"    [INFO]\t\tMODEL TRAINING")
    print(f"    [INFO]\t{'=' * 50}")
    history = model.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS, shuffle=True)

    # Save the trained model to run inference on
    model.save(MODEL_SAVE_PATH)

    # Save model scores in arrays
    accuracy_scores = history.history['acc']
    loss_scores = history.history['loss']

    np.save(ACCURACY_PATH, accuracy_scores)
    np.save(LOSS_PATH, loss_scores)

    print(f"\n    [INFO]\tDone!")


if __name__ == "__main__":
    main()
