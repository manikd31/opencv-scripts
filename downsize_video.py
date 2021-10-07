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
from constants import TEST_PATH_IN
from constants import TEST_PATH_OUT
from constants import TEST_TARGET_FPS
from constants import VIDEO_EXT


def parse_video(path_in: str,
                path_out: str,
                file_name: str,
                target_fps: float):
    """
    Helper method to get VideoCapture properties for the given video.

    :param path_in:
        Path to the video to downsize
    :param path_out:
        Path to save the downsized video
    :param file_name:
        Name of the video file to downsize
    :param target_fps:
        Target FPS for downsizing video
    """

    cap = cv2.VideoCapture(path_in)
    if target_fps >= cap.get(PROP_ID_FPS):
        print(f"    [INFO]\tTarget FPS is equal to or larger than source FPS, skipping video")
        return

    new_file_name = f"{file_name.split('.')[0]}_downsized_at_fps={int(target_fps)}{VIDEO_EXT}"

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
    cap.release()


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
        'message': 'Do you wish to process the complete folder or a selected videos?',
        'choices': [
            'Complete Folder',
            'Select Videos'
        ]
    })
    is_dir = answer_is_dir['is_dir'] == "Complete Folder"

    if is_dir:
        file_names = os.listdir(path_in)
    else:
        answer_file_names = prompt({
            'type': 'checkbox',
            'name': 'file_names',
            'message': 'Select the videos to downsize: ',
            'choices': [{'name': _file} for _file in os.listdir(path_in)]
        })
        file_names = answer_file_names['file_names']

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
    num_videos = len(file_names)
    print(f"    [INFO]\tFound {num_videos} videos.")
    for _id, video in enumerate(file_names):
        video_path = os.path.join(path_in, video)
        print(f"    [INFO]\t({_id + 1}/{num_videos})  Processing video \"{video}\"")
        parse_video(video_path, path_out, video, target_fps)

    print("    [INFO]\tDone!")


if __name__ == "__main__":
    main()
