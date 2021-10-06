"""
Script to record a video and save at desired location on local system.

Usage:
    record_video.py
    record_video.py (-h | --help)
"""

from PyInquirer import prompt
from typing import Tuple
import cv2
import os
import time

from constants import FPS16
from constants import FPS24
from constants import FPS30
from constants import FOURCC
from constants import STD_DIMENSIONS
from constants import TEST_PATH_IN
from constants import VIDEO_EXT

FONT_STYLE = cv2.FONT_HERSHEY_PLAIN


def change_res(cap: cv2.VideoCapture,
               width: int,
               height: int):
    """
    Helper method to set the video resolution for the current VideoCapture object.

    :param cap:
        The current VideoCapture source object
    :param width:
        Desired width of the output video
    :param height:
        Desired height of the output video
    """

    cap.set(3, width)
    cap.set(4, height)


def get_dims(cap: cv2.VideoCapture,
             res: str = '480p') -> Tuple[int, int]:
    """
    Helper method to get the appropriate dimensions of the video based on desired resolution.

    :param cap:
        VideoCapture source object
    :param res:
        Desired resolution, one of ('480p', '720p', '1080p')
    :return:
        The desired width and height for the output video
    """

    width, height = STD_DIMENSIONS['480p']
    if res in STD_DIMENSIONS:
        width, height = STD_DIMENSIONS[res]
    change_res(cap, width, height)

    return width, height


def find_closest_fps(_fps: float) -> float:
    """
    Helper method to find the closest FPS value to the recorded FPS.

    :param _fps:
        Recorded FPS
    :return:
        Closest FPS to save video file
    """

    if _fps <= FPS24:
        video_fps = FPS24 if abs(FPS24 - _fps) <= abs(FPS16 - _fps) else FPS16
    else:
        video_fps = FPS24 if abs(FPS24 - _fps) <= abs(FPS30 - _fps) else FPS30

    return video_fps


def process_display_time(start_time: time.time,
                         current_time: time.time) -> str:
    """
    Helper method to parse time elapsed into the format hh:mm:ss.

    :param start_time:
        The start time of the recording
    :param current_time:
        The current time to get total time elapsed (in seconds)
    :return:
        The final string to print in the given hh:mm:ss format
    """

    time_span = current_time - start_time
    seconds = int(time_span % 60)
    minutes = int(time_span // 60)
    hours = int(time_span // 3600)

    if seconds < 10:
        seconds = f"0{str(seconds)}"
    if minutes < 10:
        minutes = f"0{str(minutes)}"
    if hours < 10:
        hours = f"0{str(hours)}"

    return f"{hours}:{minutes}:{seconds}"


def main():
    """Main body of the script to be run."""

    answer_video_res = prompt({
        'type': 'list',
        'name': 'video_res',
        'message': 'Select the video resolution',
        'choices': [
            '480p',
            '720p',
            '1080p'
        ],
    })
    video_res = answer_video_res['video_res']

    answer_path_out = prompt({
        'type': 'input',
        'name': 'path_out',
        'message': 'Enter the path to save video to: ',
        'default': TEST_PATH_IN
    })
    path_out = answer_path_out['path_out']

    answer_video_name = prompt({
        'type': 'input',
        'name': 'video_name',
        'message': 'Enter the video name: ',
        'default': 'video.mp4'
    })
    video_name = answer_video_name['video_name']

    if len(video_name.split('.')) < 2:
        video_name += VIDEO_EXT

    capture = cv2.VideoCapture(0)
    dims = get_dims(capture, video_res)

    frames = []
    start_time = time.time()
    fps_time = start_time

    os.makedirs(path_out, exist_ok=True)
    while True:
        _, frame = capture.read()
        frame = cv2.flip(frame, 1)
        frames.append(frame.copy())
        current_time = time.time()
        time_elapsed = process_display_time(start_time, current_time)

        cv2.putText(frame, f"fps: {int(1 / (current_time - fps_time))}", (20, 40), FONT_STYLE, 2, (0, 255, 0), 2)
        cv2.putText(frame, f"{time_elapsed}", (int(0.75 * dims[0]), dims[1] - 20), FONT_STYLE, 2, (255, 255, 255), 2)
        fps_time = current_time
        cv2.imshow("Video", frame)

        if cv2.waitKey(1) == ord('q'):
            break

    end_time = time.time()

    _fps = round(len(frames) / int(end_time - start_time))
    fps = find_closest_fps(_fps)

    out = cv2.VideoWriter(os.path.join(path_out, video_name), FOURCC, fps, dims)
    print(f"    [INFO]\tSaving file at {os.path.join(path_out, video_name)}")

    for frame in frames:
        out.write(frame)

    cv2.destroyAllWindows()
    capture.release()
    out.release()


if __name__ == "__main__":
    main()
