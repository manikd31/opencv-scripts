"""
Script to record videos and save at desired location on local system.

Usage:
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


def record_videos(path_out: str,
                  video_name: str,
                  video_res: str):
    """
    Helper method to record multiple videos and end script on pressing "Q".

    :param path_out:
        Path to save the video(s) to
    :param video_name:
        Name of the video to save
    :param video_res:
        Video resolution to use while saving the video
    """

    cap = cv2.VideoCapture(0)
    dims = get_dims(cap, video_res)

    video_num = 0
    video_name_num = f"{video_name}_{video_num}.mp4"      # video_name : sample_video_0.mp4
    while video_name_num in os.listdir(path_out):
        video_num += 1
        video_name_num = f"{video_name}_{video_num}.mp4"

    out = None
    is_recording = False
    start_time = time.time()

    while True:
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        frame_copy = frame.copy()

        cv2.putText(frame, f"R : Start recording", (dims[0] - 300, dims[1] - 60), FONT_STYLE, 1.5, (255, 255, 255), 2)
        cv2.putText(frame, f"E : End recording", (dims[0] - 300, dims[1] - 40), FONT_STYLE, 1.5, (255, 255, 255), 2)
        cv2.putText(frame, f"Q : Quit", (dims[0] - 300, dims[1] - 20), FONT_STYLE, 1.5, (255, 255, 255), 2)

        key_press = cv2.waitKey(1) & 0xff

        # Hit "R" to start recording
        if key_press == ord('r') and not is_recording:
            start_time = time.time()
            is_recording = True
            path_to_save = os.path.join(path_out, video_name_num)
            out = cv2.VideoWriter(path_to_save, FOURCC, FPS30, dims)

        # Hit "E" to end recording
        if key_press == ord('e') and is_recording:
            is_recording = False
            video_num += 1
            video_name_num = f"{video_name}_{video_num}.mp4"

        if is_recording:
            out.write(frame_copy)
            time_elapsed = process_display_time(start_time, time.time())
            cv2.putText(frame, f"Recording : {video_name_num}", (20, 40), FONT_STYLE, 1.5, (255, 255, 255), 2)
            cv2.putText(frame, f"{time_elapsed}", (20, dims[1] - 20), FONT_STYLE, 1.5, (255, 255, 255), 2)
        else:
            cv2.putText(frame, f"Not recording", (20, 40), FONT_STYLE, 1.5, (255, 255, 255), 2)

        # Hit "Q" to terminate script
        if key_press == ord('q'):
            cv2.destroyAllWindows()
            break

        cv2.imshow("Video", frame)

    cap.release()
    if out:
        out.release()


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

    os.makedirs(path_out, exist_ok=True)
    video_name = video_name.split('.')[0]
    record_videos(path_out, video_name, video_res)


if __name__ == "__main__":
    main()
