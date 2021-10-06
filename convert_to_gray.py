"""
Script to convert RGB video to Grayscale.

Usage:
    convert_to_gray.py (-h | --help)
"""

from PyInquirer import prompt
import cv2
import os

from constants import FOURCC
from constants import PROP_ID_FPS
from constants import PROP_ID_HEIGHT
from constants import PROP_ID_WIDTH
from constants import TEST_PATH_IN
from constants import TEST_PATH_OUT
from constants import VIDEO_EXT

IS_COLOR = False


def convert_to_gray(path_in: str,
                    path_out: str):
    """
    Method to convert given source video from COLOR to GRAYSCALE and save at destination.

    :param path_in:
        Path to the video file to convert to grayscale
    :param path_out:
        Path to save the converted video at
    """

    cap = cv2.VideoCapture(path_in)
    out = cv2.VideoWriter(path_out, FOURCC, cap.get(PROP_ID_FPS),
                          (int(cap.get(PROP_ID_WIDTH)), int(cap.get(PROP_ID_HEIGHT))), IS_COLOR)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        out.write(frame)

    cap.release()
    out.release()


def main():
    """Main body of the script to be run."""

    answer_path_in = prompt({
        'type': 'input',
        'name': 'path_in',
        'message': 'Enter the path to the videos directory: ',
        'default': TEST_PATH_IN
    })
    path_in = answer_path_in['path_in']
    if not os.path.isdir(path_in):
        print(f"    [ERROR]\tThe folder \"{path_in}\" doesn't exist.")
        return

    answer_is_dir = prompt({
        'type': 'list',
        'name': 'is_dir',
        'message': 'Do you wish to process the complete folder or selected videos?',
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
            'message': 'Select the videos to convert to grayscale: ',
            'choices': [{'name': _file} for _file in os.listdir(path_in)]
        })
        file_names = answer_file_names['file_names']

    answer_path_out = prompt({
        'type': 'input',
        'name': 'path_out',
        'message': 'Enter the path to save the converted videos to: ',
        'default': TEST_PATH_OUT
    })
    path_out = answer_path_out['path_out']

    os.makedirs(path_out, exist_ok=True)
    num_videos = len(file_names)
    print(f"    [INFO]\tFound {num_videos} videos.")
    for _id, video in enumerate(file_names):
        print(f"    [INFO]\t({_id + 1}/{num_videos})  Processing video \"{video}\"")
        video_path = os.path.join(path_in, video)
        grayscale_video_name = f"{video.split('.')[0]}_grayscale{VIDEO_EXT}"
        save_path = os.path.join(path_out, grayscale_video_name)
        convert_to_gray(video_path, save_path)

    print("    [INFO]\tDone!")


if __name__ == "__main__":
    main()
