"""
Script to run output test window for final testing.

Usage:
    test_output.py [--dataset=DATASET]
    test_output.py (-h | --help)

Options:
    --dataset=DATASET   Select the dataset to get the trained model (MNIST or ASL)
"""

from docopt import docopt
from keras.models import load_model
from typing import Tuple
import cv2
import numpy as np
import os

from constants import DATASETS
from constants import INT2LAB
from constants import MODEL_BASE_PATH
from constants import STD_COLORS
from process_output import process_output

FONT_STYLE = cv2.FONT_HERSHEY_PLAIN


def put_background(frame: np.ndarray,
                   top_left: Tuple[int, int],
                   bottom_right: Tuple[int, int],
                   alpha: float = 0.4,
                   color: str = 'Black') -> np.ndarray:
    """
    Helper method to add a grayed out background rectangle to emphasize more on foreground text.

    :param frame:
        The VideoCapture frame to add the rectangle to
    :param top_left:
        The x and y coordinates of the top-left corner of rectangle
    :param bottom_right:
        The x and y coordinates of the bottom-tight corner of rectangle
    :param alpha:
        The weight of darkness of the background rectangle
    :param color:
        The color to fill the background with
    :return:
        The final frame with the rectangle.
    """

    color = STD_COLORS[color]
    (x, y), (w, h) = top_left, bottom_right
    sub_img = frame[y:y + h, x:x + w]
    beta = 1.0 - alpha

    color_rect = cv2.rectangle(sub_img.copy(), top_left, bottom_right, color, cv2.FILLED)
    res = cv2.addWeighted(sub_img, beta, color_rect, alpha, 0.0)
    frame[y:y + h, x:x + w] = res

    return frame


def put_bbox(frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Put a bounding box to get portion of the stream to test on.

    :param frame:
        The VideoCapture frame to add the bounding-box to
    :return:
        The final frame with the bounding-box, and the predicted class
    """

    # Bounding-box outline color
    color = STD_COLORS['Pink']

    frame_copy = frame.copy()
    mid_y, mid_x = frame.shape[0] // 2, frame.shape[1] // 2
    sub_img = frame_copy[mid_y - 140:mid_y + 140, mid_x:mid_x + 280]

    # Add blur to background except the bounding-box
    frame = put_background(frame, (0, 0), (frame.shape[1], frame.shape[0]), alpha=0.65)
    frame[mid_y - 140:mid_y + 140, mid_x:mid_x + 280] = sub_img
    cv2.rectangle(frame, (mid_x, mid_y - 140), (mid_x + 280, mid_y + 140), color, 2, cv2.LINE_AA)

    return frame, sub_img


def main():
    """Main body of the script to be run."""

    args = docopt(__doc__)
    dataset = args["--dataset"] or "MNIST"

    if dataset not in DATASETS.keys():
        print(f"    [INFO]\t\"{dataset} not in the list of datasets trained on.\"")
        return

    cap = cv2.VideoCapture(0)

    use_int2lab = False
    if dataset == "ASL":
        use_int2lab = True

    # Load the saved model
    model_select = DATASETS[dataset]
    MODEL_PATH = os.path.join(MODEL_BASE_PATH, model_select)

    model = load_model(MODEL_PATH)

    while True:
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        frame, sub_img = put_bbox(frame)

        # Do post-processing and prediction on "sub_img"
        prediction = process_output(model, sub_img)

        # Convert int label to alphabet if ASL dataset is selected
        if use_int2lab:
            prediction = INT2LAB[prediction]

        cv2.putText(frame, f"Predicted : {prediction}", (10, 30), FONT_STYLE, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Video", frame)

        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break

    cap.release()


if __name__ == "__main__":
    main()
