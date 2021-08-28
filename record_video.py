"""
Script to record a video and save at desired location on local system.

Usage:
    record_video.py
    record_video.py (-h | --help)
"""

import cv2
import os
from PyInquirer import prompt
import time

path_out = r'C:\Users\Manik\Desktop\test_CV_videos'

FPS16 = 16.0
FPS24 = 24.0
FPS30 = 30.0

STD_DIMENSIONS = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
}
VIDEO_TYPE = [
    'mp4',
    'avi'
]
FOURCC = 0x7634706d


def change_res(cap, width, height):
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


def get_dims(cap, res='480p'):
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


def find_closest_fps(_fps):
    """
    Helper method to find the closest FPS value to the recorded FPS.

    :param _fps:
        Recorded FPS
    :return:
        Closes FPS to save video file
    """

    if _fps <= FPS24:
        video_fps = FPS24 if abs(FPS24 - _fps) <= abs(FPS16 - _fps) else FPS16
    else:
        video_fps = FPS24 if abs(FPS24 - _fps) <= abs(FPS30 - _fps) else FPS30

    return video_fps


def main():
    """Main body of the script to be run."""

    answer_video_res = prompt({
        'type': 'list',
        'name': 'video_res',
        'message': 'Select the video resolution',
        'choices': [
            '480p',
            '720p'
        ],
    })
    video_res = answer_video_res['video_res']

    answer_video_name = prompt({
        'type': 'input',
        'name': 'video_name',
        'message': 'Enter the video name: ',
        'default': 'video.mp4'
    })
    video_name = answer_video_name['video_name']

    if len(video_name.split('.')) < 2 or video_name.split('.')[1] not in VIDEO_TYPE:
        answer_video_ext = prompt({
            'type': 'list',
            'name': 'video_ext',
            'message': 'Select the video extension',
            'choices': [
                '.mp4',
                '.avi'
            ],
        })
        video_name += answer_video_ext['video_ext']

    capture = cv2.VideoCapture(0)
    dims = get_dims(capture, video_res)

    frames = []
    s_time = time.time()
    p_time = s_time

    os.makedirs(path_out, exist_ok=True)
    while True:
        _, frame = capture.read()
        frame = cv2.flip(frame, 1)
        frames.append(frame.copy())
        c_time = time.time()

        cv2.putText(frame, f"fps: {int(1 / (c_time - s_time))}", (20, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        s_time = c_time
        cv2.imshow("Video", frame)

        if cv2.waitKey(1) == ord('q'):
            break

    f_time = time.time()

    _fps = round(len(frames) / int(f_time - p_time))
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
