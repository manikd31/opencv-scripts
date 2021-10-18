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

    answer_is_dataset = prompt({
        'type': 'list',
        'name': 'is_dataset',
        'message': 'Do you wish to process the complete dataset or selected folders?',
        'choices': [
            'Complete Dataset',
            'Select Folders'
        ]
    })
    is_dataset = answer_is_dataset['is_dataset'] == "Complete Dataset"

    if is_dataset:
        folder_names = os.listdir(path_in)
    else:
        answer_folder_names = prompt({
            'type': 'checkbox',
            'name': 'folder_names',
            'message': 'Select the folders to process: ',
            'choices': [{'name': _file} for _file in os.listdir(path_in)]
        })
        folder_names = answer_folder_names['folder_names']

    answer_path_out = prompt({
        'type': 'input',
        'name': 'path_out',
        'message': 'Enter the path to save the converted videos to: ',
        'default': TEST_PATH_OUT
    })
    path_out = answer_path_out['path_out']

    os.makedirs(path_out, exist_ok=True)

    num_folders = len(folder_names)
    print(f"    [INFO]\tFound {num_folders} folders.")
    for folder_id, folder in enumerate(folder_names):
        print(f"    [INFO]\t({folder_id + 1}/{num_folders})\tProcessing folder \"{folder}\"")
        folder_path = os.path.join(path_in, folder)
        new_folder_path = os.path.join(path_out, folder)
        os.makedirs(new_folder_path, exist_ok=True)

        answer_is_dir = prompt({
            'type': 'list',
            'name': 'is_dir',
            'message': f'Do you wish to process the complete folder \"{folder.upper()}\" or selected videos?',
            'choices': [
                'Complete Folder',
                'Select Videos'
            ]
        })
        is_dir = answer_is_dir['is_dir'] == "Complete Folder"

        if is_dir:
            file_names = os.listdir(folder_path)
        else:
            answer_file_names = prompt({
                'type': 'checkbox',
                'name': 'file_names',
                'message': 'Select the videos to convert to grayscale: ',
                'choices': [{'name': _file} for _file in os.listdir(folder_path)]
            })
            file_names = answer_file_names['file_names']

        num_videos = len(file_names)
        print(f"    [INFO]\t\tFound {num_videos} videos.")
        for video_id, video in enumerate(file_names):
            print(f"    [INFO]\t\t({video_id + 1}/{num_videos})\tProcessing video \"{video}\"")
            video_path = os.path.join(folder_path, video)
            flipped_name = f"{video.split('.')[0]}_grayscale{VIDEO_EXT}"
            save_path = os.path.join(new_folder_path, flipped_name)
            convert_to_gray(video_path, save_path)

    print("    [INFO]\tDone!")


if __name__ == "__main__":
    main()
