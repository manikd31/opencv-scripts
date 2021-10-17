"""
Helper script to process videos inside a folder and flip them horizontally to double the size of the data-set.

Usage:
    flip_video.py (-h | --help)
"""

import os
import cv2
from PyInquirer import prompt

from constants import FOURCC
from constants import PROP_ID_FPS
from constants import PROP_ID_HEIGHT
from constants import PROP_ID_WIDTH
from constants import TEST_PATH_IN
from constants import TEST_PATH_OUT
from constants import VIDEO_EXT


def flip_video(path_in: str,
               path_out: str):
    """
    Horizontally flip the video at the given source and save at the destination.

    :param path_in:
        Path to the video to be flipped
    :param path_out:
        Path to save the flipped video
    """

    cap = cv2.VideoCapture(path_in)
    out = cv2.VideoWriter(path_out, FOURCC, cap.get(PROP_ID_FPS),
                          (int(cap.get(PROP_ID_WIDTH)), int(cap.get(PROP_ID_HEIGHT))))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        out.write(frame)

    cap.release()
    out.release()


def main():
    """Main body of the script to be run."""

    answer_path_in = prompt({
        'type': 'input',
        'name': 'path_in',
        'message': 'Enter the path to the dataset directory: ',
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
        'message': 'Enter the path to save the flipped videos to: ',
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
                'message': 'Select the videos to flip horizontally: ',
                'choices': [{'name': _file} for _file in os.listdir(folder_path)]
            })
            file_names = answer_file_names['file_names']

        num_videos = len(file_names)
        print(f"    [INFO]\t\tFound {num_videos} videos.")
        for video_id, video in enumerate(file_names):
            print(f"    [INFO]\t\t({video_id + 1}/{num_videos})\tProcessing video \"{video}\"")
            video_path = os.path.join(folder_path, video)
            flipped_name = f"{video.split('.')[0]}_flipped{VIDEO_EXT}"
            save_path = os.path.join(new_folder_path, flipped_name)
            flip_video(video_path, save_path)

    print("    [INFO]\tDone!")


if __name__ == "__main__":
    main()