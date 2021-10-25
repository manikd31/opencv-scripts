"""
Script to run the selected data augmentation techniques and create a new augmented data-set.

Usage:
    augment_dataset.py (-h | --help)
"""

from PyInquirer import prompt
import os
import shutil

from constants import AUGMENTATION_METHODS
from constants import TEST_PATH_IN
from constants import TEST_PATH_OUT
from constants import TEST_TARGET_FPS
from constants import VIDEO_EXT

from blur_video import blur_video
from convert_to_gray import convert_to_gray
from downsize_video import parse_video
from flip_video import flip_video
from invert_color import invert_color


def augment_dataset(path_in: str,
                    path_out: str,
                    method: str):
    """
    Helper method to create an augmented data-set from the options given as data augmentation techniques.

    :param path_in:
        Path to the video to process
    :param path_out:
        Path to save the augmented video to
    :param method:
        The type of augmentation method to be used
    """

    if method.lower() == "blurred":         # Blur video, and save
        blur_video(path_in, path_out)
    elif method.lower() == "inv_color":     # Invert colors of video, and save
        invert_color(path_in, path_out)
    elif method.lower() == "flipped":       # Flip video horizontally, and save
        flip_video(path_in, path_out)
    else:                                   # Convert video to grayscale, and save
        convert_to_gray(path_in, path_out)


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
            'message': 'Select the videos to invert colors of: ',
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

    answer_augmentation_methods = prompt({
        'type': 'checkbox',
        'name': 'augmentation_methods',
        'message': 'Select the data augmentation methods to apply on raw videos.',
        'choices': [{'name': method} for method in AUGMENTATION_METHODS.keys()]
    })
    augmentation_methods = answer_augmentation_methods['augmentation_methods']

    os.makedirs(path_out, exist_ok=True)
    num_videos = len(file_names)
    print(f"    [INFO]\tFound {num_videos} videos.")
    for _id, video in enumerate(file_names):
        print(f"    [INFO]\t({_id + 1}/{num_videos})\tProcessing video \"{video}\"")
        video_path = os.path.join(path_in, video)
        shutil.copy(video_path, path_out)
        for augmentation in augmentation_methods:
            method = AUGMENTATION_METHODS.get(augmentation)
            augmented_video_name = f"{video.split('.')[0]}_{method}{VIDEO_EXT}"
            save_path = os.path.join(path_out, augmented_video_name)
            augment_dataset(video_path, save_path, method)

    print()

    answer_downsize = prompt({
        'type': 'list',
        'name': 'downsize',
        'message': 'Do you also want to downsize all the videos?',
        'choices': [
            'YES',
            'NO'
        ]
    })
    do_downsize = True if answer_downsize['downsize'] == "YES" else False

    if do_downsize:
        downsize_path = os.path.join(path_out, "downsized_videos")
        os.makedirs(downsize_path, exist_ok=True)

        print(f"    [INFO]\tDownsizing videos now ...")
        num_videos = len(os.listdir(path_out))
        print(f"    [INFO]\tFound {num_videos - 1} videos.")
        for _id, source_video in enumerate(os.listdir(path_out)):
            if _id == 0:
                continue
            print(f"    [INFO]\t({_id}/{num_videos - 1})\tProcessing video \"{source_video}\"")
            video_in = os.path.join(path_out, source_video)
            parse_video(video_in, downsize_path, float(TEST_TARGET_FPS))

    print("    [INFO]\tDone!")


if __name__ == "__main__":
    main()
