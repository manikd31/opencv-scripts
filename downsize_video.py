"""
Script to downsize a video, i.e. reduce the fps of any video with a target fps value.

Usage:
    downsize_video.py
    downsize_video.py (-h | --help)
"""

from PyInquirer import prompt
import cv2
import os

from constants import FOURCC
from constants import PROP_ID_FPS
from constants import PROP_ID_FRAME_COUNT
from constants import PROP_ID_HEIGHT
from constants import PROP_ID_WIDTH
from constants import TEST_FILE_NAME
from constants import TEST_PATH_IN
from constants import TEST_PATH_OUT
from constants import TEST_TARGET_FPS
from constants import VIDEO_EXT


def parse_video(cap : cv2.VideoCapture,
                path_out: str,
                file_name: str,
                target_fps: float):
    """
    Helper method to get VideoCapture properties for the given video.

    :param cap:
        VideoCapture object for the video
    :param path_out:
        Path to save the downsized video
    :param file_name:
        Name of the video file to downsize
    :param target_fps:
        Target FPS for downsizing video
    """

    new_file_name = f"{file_name.split('.')[0]}_downsized_at_fps={int(target_fps)}.{VIDEO_EXT}"

    width = int(cap.get(PROP_ID_WIDTH))
    height = int(cap.get(PROP_ID_HEIGHT))
    current_fps = int(cap.get(PROP_ID_FPS))
    frame_count = int(cap.get(PROP_ID_FRAME_COUNT))
    frame_jump = current_fps / target_fps

    out = cv2.VideoWriter(os.path.join(path_out, new_file_name), FOURCC, target_fps, (width, height))

    curr_frame = 0
    prev_frame_idx = -1
    while curr_frame < frame_count:
        new_frame_idx = int(curr_frame * frame_jump)
        if new_frame_idx != prev_frame_idx:
            cap.set(1, new_frame_idx)
            _, frame = cap.read()
            out.write(frame)
            prev_frame_idx = new_frame_idx
        curr_frame += 1

    out.release()


def main():
    """Main body of the script to be run."""

    answer_path_in = prompt({
        'type': 'input',
        'name': 'path_in',
        'message': 'Enter the path to the videos folder: ',
        'default': TEST_PATH_IN
    })
    path_in = answer_path_in['path_in']
    if not os.path.isdir(path_in):
        print(f"    [ERROR]\tThe folder \"{path_in}\" doesn't exist.")
        return

    answer_is_dir = prompt({
        'type': 'list',
        'name': 'is_dir',
        'message': 'Do you wish to process the complete folder or a single video?',
        'choices': [
            'Complete Folder',
            'Single Video'
        ]
    })
    is_dir = answer_is_dir['is_dir'] == "Complete Folder"

    answer_path_out = prompt({
        'type': 'input',
        'name': 'path_out',
        'message': 'Enter the path to save the downsized video(s) to: ',
        'default': TEST_PATH_OUT
    })
    path_out = answer_path_out['path_out']

    answer_target_fps = prompt({
        'type': 'input',
        'name': 'target_fps',
        'message': 'Enter the target FPS for the video(s): ',
        'default': str(TEST_TARGET_FPS)
    })
    target_fps = float(answer_target_fps['target_fps'])

    os.makedirs(path_out, exist_ok=True)
    if not is_dir:
        answer_file_name = prompt({
            'type': 'input',
            'name': 'file_name',
            'message': 'Enter the name of the video to downsize: ',
            'default': TEST_FILE_NAME
        })
        file_name = answer_file_name['file_name']
        if not os.path.isfile(os.path.join(path_in, file_name)):
            print(f"    [ERROR]\tThe file \"{file_name}\" or folder \"{path_in}\" doesn't exist.")
        else:
            video_path = os.path.join(path_in, file_name)
            capture = cv2.VideoCapture(video_path)
            if target_fps >= capture.get(PROP_ID_FPS):
                print(f"    [INFO]\tTarget FPS is equal to or larger than source FPS, skipping video.")
            else:
                parse_video(capture, path_out, file_name, target_fps)
                print("    [INFO]\tDone!")
            capture.release()
    else:
        num_videos = len(os.listdir(path_in))
        print(f"    [INFO]\tFound {num_videos} videos.")
        for _id, video in enumerate(os.listdir(path_in)):
            video_path = os.path.join(path_in, video)
            capture = cv2.VideoCapture(video_path)
            if target_fps >= capture.get(PROP_ID_FPS):
                print(f"    [INFO]\tTarget FPS is equal to or larger than source FPS, skipping video {_id + 1}")
            else:
                print(f"    [INFO]\t({_id + 1}/{num_videos})  Processing video \"{video}\"")
                parse_video(capture, path_out, video, target_fps)
            capture.release()
        print("    [INFO]\tDone!")


if __name__ == "__main__":
    main()
