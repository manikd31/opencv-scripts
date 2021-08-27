"""
Script to run output test window for final testing.

Usage:
    test_output.py
    test_output.py (-h | --help)
"""

import cv2
import numpy as np

FONT_STYLE = cv2.FONT_HERSHEY_PLAIN


def put_background(frame, alpha, x, y, w, h):
    """
    Helper method to add a grayed out background rectangle to emphasize more on foreground text.

    :param frame:
        The VideoCapture frame to add the rectangle to
    :param alpha:
        The weight of darkness of the background rectangle
    :param x:
        Top-left x-coordinate (starting point)
    :param y:
        Top-left y-coordinate (starting point)
    :param w:
        Bottom-right x-coordinate (width)
    :param h:
        Bottom-right y-coordinate (height)
    :return:
        The final frame with the rectangle.
    """

    sub_img = frame[y:y + h, x:x + w]
    beta = 1.0 - alpha
    black_rect = np.zeros(sub_img.shape, dtype=np.uint8)
    res = cv2.addWeighted(sub_img, beta, black_rect, alpha, 0.0)
    frame[y:y + h, x:x + w] = res

    return frame


def main():
    cap = cv2.VideoCapture(0)
    # cap.set(3, 1280)
    # cap.set(4, 720)
    while True:
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)

        x, y, w, h = 0, 0, frame.shape[1], 50
        alpha = 0.7
        frame = put_background(frame, alpha, x, y, w, h)
        cv2.putText(frame, f"{frame.shape}", (10, 30), FONT_STYLE, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Video", frame)

        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break

    cap.release()


if __name__ == "__main__":
    main()
