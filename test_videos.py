"""
Script to select saved model and run on test-videos to get testing accuracy.

Test videos directory should be of the following format:

    /path-to-test-videos/
        |--- class_1
        |   |--- video_1.mp4
        |   |--- ...
        |   |--- video_n.mp4
        |
        |--- class_2
        |   |--- video_1.mp4
        |   |--- ...
        |   |--- video_n.mp4
        |
        |--- ...
        |
        |--- class_c
        |   |--- video_1.mp4
        |   |--- ...
        |   |--- video_n.mp4
        ---------------------

Usage:
    test_videos.py (-h | --help)
"""

import os

from natsort import natsorted
from natsort import ns
from PyInquirer import prompt
import cv2
import keras
import numpy as np

from constants import TEST_PATH_TEST_VIDEOS, TEST_SAVED_MODELS_DIRECTORY


def main():
    """Main body."""
    answer_test_videos_dir = prompt({
        'type': 'input',
        'name': 'test_videos_dir',
        'message': 'Enter the path to test-videos directory: ',
        'default': TEST_PATH_TEST_VIDEOS
    })
    test_videos_dir = answer_test_videos_dir['test_videos_dir']
    if not os.path.isdir(test_videos_dir):
        print(f"    [ERROR]\tThe folder \"{test_videos_dir}\" doesn't exist.")
        return

    answer_saved_models_dir = prompt({
        'type': 'input',
        'name': 'saved_models_dir',
        'message': 'Enter the path to saved models directory: ',
        'default': TEST_SAVED_MODELS_DIRECTORY
    })
    saved_models_dir = answer_saved_models_dir['saved_models_dir']
    saved_models = natsorted(os.listdir(saved_models_dir), alg=ns.IC)

    answer_model_weights = prompt({
        'type': 'list',
        'name': 'model_weights',
        'message': 'Select the model weights to use for testing',
        'choices': saved_models
    })
    model_weights = answer_model_weights['model_weights']
    model_weights_path = os.path.join(saved_models_dir, model_weights)
    model = keras.models.load_model(model_weights_path)

    print()
    print(f"    [INFO]\t{'=' * 50}")
    print(f"    [INFO]\t\t\tMODEL SUMMARY")
    print(f"    [INFO]\t{'=' * 50}")
    print(model.summary())
    print()

    class_names = natsorted(os.listdir(test_videos_dir), alg=ns.IC)
    lab2int_mapping = dict()
    int2lab_mapping = dict()
    _idx = 0
    for class_name in class_names:
        lab2int_mapping[class_name] = _idx
        int2lab_mapping[_idx] = class_name
        _idx += 1

    print()
    print(f"    [INFO]\t{'=' * 50}")
    print(f"    [INFO]\t\t\tMODEL PERFORMANCE")
    print(f"    [INFO]\t{'=' * 50}")

    total_samples = 0
    correct_samples = 0
    for class_name in class_names:
        class_path = os.path.join(test_videos_dir, class_name)
        class_actual = []
        class_predictions = []
        videos_list = natsorted(os.listdir(class_path), alg=ns.IC)
        for video in videos_list:
            video_path = os.path.join(class_path, video)
            cap = cv2.VideoCapture(video_path)
            frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = np.flip(frame, axis=-1)
                frames.append(frame)
            cap.release()
            frames = np.array(frames)
            frames = np.expand_dims(frames, axis=0)

            prediction = np.argmax(model.predict(frames))
            class_predictions.append(prediction)
            class_actual.append(lab2int_mapping[class_name])

        correct_per_class = 0
        samples_per_class = len(class_predictions)
        total_samples += samples_per_class
        for actual, predicted in zip(class_actual, class_predictions):
            if actual == predicted:
                correct_per_class += 1
        correct_samples += correct_per_class

        class_accuracy = round(correct_per_class / samples_per_class, 4)
        if len(class_name) <= 6:
            print(f"    [INFO]\tClass: \"{class_name}\"\t\t\tAccuracy: {class_accuracy}")
        else:
            print(f"    [INFO]\tClass: \"{class_name}\"\t\tAccuracy: {class_accuracy}")
        print(f"    [INFO]\t{'-' * 50}")
    overall_accuracy = round(correct_samples / total_samples, 4)
    print(f"    [INFO]")
    print(f"    [INFO]\t{'=' * 50}")
    print(f"    [INFO]\t\tModel Testing Accuracy: {overall_accuracy}")
    print(f"    [INFO]\t{'=' * 50}")

    print(f"    [INFO]")
    print(f"    [INFO]\tDone!")


if __name__ == "__main__":
    main()