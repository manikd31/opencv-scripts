"""
Script to run output test window for final testing.

Usage:
    test_output.py
    test_output.py (-h | --help)
"""
from typing import Tuple
from PyInquirer import prompt
import cv2
import numpy as np

FONT_STYLE = cv2.FONT_HERSHEY_PLAIN
STD_COLORS = {
    'black': (0, 0, 0),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'red': (0, 0, 255),
    'cyan': (255, 255, 0),
    'yellow': (0, 255, 255),
    'pink': (255, 0, 255),
    'white': (255, 255, 255)
}


def put_background(frame: np.ndarray,
                   top_left: Tuple[int, int],
                   bottom_right: Tuple[int, int],
                   alpha: float = 0.4,
                   color: str = 'black') -> np.ndarray:
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


def main():
    answer_bg_color = prompt({
        'type': 'list',
        'name': 'bg_color',
        'message': 'Select the background color',
        'choices': list(STD_COLORS.keys())
    })
    bg_color = answer_bg_color['bg_color']

    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)

        x, y, w, h = 0, 0, frame.shape[1], 50
        frame = put_background(frame, (x, y), (x + w, y + h), color=bg_color)
        cv2.putText(frame, f"{frame.shape}", (10, 30), FONT_STYLE, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Video", frame)

        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break

    cap.release()


if __name__ == "__main__":
    main()
