import keras
import numpy as np
import cv2
import os


def process_output(model: keras.models.Sequential, frame: np.ndarray) -> int:
    """
    Process the current frame from the trained model and return output class.

    :param model:
        The saved model weights to get predictions
    :param frame:
        The VideoCapture frame to process
    :return:
        The predicted class
    """

    # Resize the frame from (280 x 280 x 3) to (28 x 28 x 1)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (28, 28))
    input_frame = np.reshape(frame, (1, 28, 28, 1))

    # Get prediction
    prediction = int(np.argmax(model.predict(input_frame)))

    return prediction
