"""
Final script to run on the raw videos dataset folder. This will help create a new dataset folder
and prepare the videos to be input for training the model.

The dataset folder structure before using this script should be something as follows:

    /path-to-the-dataset/
        |--- class_1
        |   |--- video_1.mp4
        |   |--- ...
        |   |--- video_n.mp4
        |
        |--- class_2
        |   |--- video_1.mp4
        |   |--- ...
        |   |--- video_n.mp4
        |
        |--- ...
        |
        |--- class_c
        |   |--- video_1.mp4
        |   |--- ...
        |   |--- video_n.mp4
        ---------------------

Usage:
    prepare_dataset.py (-h | --help)
"""
import os
import shutil

from natsort import natsorted
from natsort import ns
from PyInquirer import prompt
import numpy as np

from augment_dataset import augment_dataset
from constants import AUGMENTATION_METHODS
from constants import TEST_NUM_TEST_VIDEOS_PER_CLASS
from constants import TEST_PATH_IN
from constants import TEST_PATH_OUT
from constants import TEST_PATH_TEST_VIDEOS
from constants import TEST_RESIZE_FRAME_HEIGHT
from constants import TEST_RESIZE_FRAME_WIDTH
from constants import TEST_TARGET_FPS
from constants import TEST_TARGET_FRAMES
from constants import VIDEO_EXT
from downsize_video import parse_video
from preprocess_videos import pad_videos
from preprocess_videos import resize_videos
from preprocess_videos import video2images


def main():
    """Main body"""

    # ----------------------------------------------------------------------------------------------
    #                       Step 1 : Get path to the raw videos directory
    # ----------------------------------------------------------------------------------------------

    answer_path_in = prompt({
        'type': 'input',
        'name': 'path_in',
        'message': 'Enter the path to the videos directory: ',
        'default': TEST_PATH_IN
    })
    path_in = answer_path_in['path_in']

    # Check if the directory exists or not
    if not os.path.isdir(path_in):
        print(f"    [ERROR]\tThe folder \"{path_in}\" doesn't exist.")
        return

    # Set to `True` to process the complete data folder
    is_dir = True

    # Get the names of the folders in the dataset (classes)
    if is_dir:
        folder_names = natsorted(os.listdir(path_in), alg=ns.IC)
    else:
        answer_folder_names = prompt({
            'type': 'checkbox',
            'name': 'folder_names',
            'message': 'Select the folders to process: ',
            'choices': [{'name': _file} for _file in natsorted(os.listdir(path_in), alg=ns.IC)]
        })
        folder_names = answer_folder_names['folder_names']

    # Get the path to save the new data folder
    answer_path_out = prompt({
        'type': 'input',
        'name': 'path_out',
        'message': 'Enter the path to save the prepared videos to: ',
        'default': TEST_PATH_OUT
    })
    path_out = answer_path_out['path_out']

    # Get the target FPS to downsize the videos
    answer_target_fps = prompt({
        'type': 'input',
        'name': 'target_fps',
        'message': 'Enter the target FPS for the downsized videos: ',
        'default': str(TEST_TARGET_FPS)
    })
    target_fps = float(answer_target_fps['target_fps'])

    # New folder inside the directory to save all downsized videos to
    downsized_path_out = os.path.join(path_out, 'downsized')
    os.makedirs(downsized_path_out, exist_ok=True)

    # Get the number of frames for constant video length
    answer_target_frames = prompt({
        'type': 'input',
        'name': 'target_frames',
        'message': 'Enter the number of frames per video for padding: ',
        'default': str(TEST_TARGET_FRAMES)
    })
    target_frames = float(answer_target_frames['target_frames'])

    # Create new directories for padded videos and respective frames
    padded_videos_directory = os.path.join(path_out, 'padded_data')
    os.makedirs(padded_videos_directory, exist_ok=True)

    answer_augmentation_methods = prompt({
        'type': 'checkbox',
        'name': 'augmentation_methods',
        'message': 'Select the data augmentation methods to apply on videos:',
        'choices': [{'name': method} for method in AUGMENTATION_METHODS.keys()]
    })
    augmentation_methods = answer_augmentation_methods['augmentation_methods']

    augmented_dataset_path = os.path.join(path_out, 'augmented_dataset')
    os.makedirs(augmented_dataset_path, exist_ok=True)

    # Get the frame size to resize the video for model training
    answer_frame_width = prompt({
        'type': 'input',
        'name': 'frame_width',
        'message': 'Enter the new frame width to resize video: ',
        'default': str(TEST_RESIZE_FRAME_WIDTH)
    })
    answer_frame_height = prompt({
        'type': 'input',
        'name': 'frame_height',
        'message': 'Enter the new frame width to resize video: ',
        'default': str(TEST_RESIZE_FRAME_HEIGHT)
    })
    frame_width = int(answer_frame_width['frame_width'])
    frame_height = int(answer_frame_height['frame_height'])
    new_dims = (frame_width, frame_height)

    answer_test_videos_dir = prompt({
        'type': 'input',
        'name': 'test_videos_dir',
        'message': 'Enter the path to test-videos directory (auto created from this script): ',
        'default': TEST_PATH_TEST_VIDEOS
    })
    test_videos_dir = answer_test_videos_dir['test_videos_dir']
    os.makedirs(test_videos_dir, exist_ok=True)

    answer_num_test_videos = prompt({
        'type': 'input',
        'name': 'num_test_videos',
        'message': 'Enter the number of test videos to be selected (per class): ',
        'default': TEST_NUM_TEST_VIDEOS_PER_CLASS
    })
    num_test_videos_per_class = int(answer_num_test_videos['num_test_videos'])

    # ----------------------------------------------------------------------------------------------
    #                           Step 2 : Downsize all videos to a target FPS
    # ----------------------------------------------------------------------------------------------

    print()
    print(f"    [INFO]\t{'='*50}")
    print(f"    [INFO]\t\t\tDOWNSIZING VIDEOS")
    print(f"    [INFO]\t{'=' * 50}")

    # # Iterate through all the folders (classes) and process all videos
    num_folders = len(folder_names)
    print(f"    [INFO]\tFound {num_folders} folders.")
    for folder_idx, folder_name in enumerate(folder_names):
        print(f"    [INFO]\t({folder_idx + 1}/{num_folders})\tProcessing folder \"{folder_name}\"")
        folder_path = os.path.join(path_in, folder_name)
        new_folder_path = os.path.join(downsized_path_out, folder_name)
        os.makedirs(new_folder_path, exist_ok=True)

        # Get all videos inside each class folder
        file_names = natsorted(os.listdir(folder_path), alg=ns.IC)
        num_videos = len(file_names)
        print(f"    [INFO]\t\tFound {num_videos} videos.")
        for video_idx, video_name in enumerate(file_names):
            print(f"    [INFO]\t\t({video_idx + 1}/{num_videos})\tProcessing video \"{video_name}\"")
            video_path_in = os.path.join(folder_path, video_name)
            video_path_out = os.path.join(new_folder_path, video_name)

            # Call the method to downsize video
            parse_video(video_path_in, video_path_out, target_fps)

    # ----------------------------------------------------------------------------------------------
    #                           Step 3 : Pad / remove frames for all videos
    # ----------------------------------------------------------------------------------------------

    print()
    print(f"    [INFO]\t{'=' * 50}")
    print(f"    [INFO]\t\t\tPADDING VIDEOS")
    print(f"    [INFO]\t{'=' * 50}")

    # Iterate through all the folders (classes) and process all videos
    for folder_idx, folder_name in enumerate(folder_names):
        print(f"    [INFO]\t({folder_idx + 1}/{num_folders})\tProcessing folder \"{folder_name}\"")
        folder_path = os.path.join(downsized_path_out, folder_name)
        new_videos_folder_path = os.path.join(padded_videos_directory, folder_name)
        os.makedirs(new_videos_folder_path, exist_ok=True)

        # Get all videos inside each class folder
        file_names = natsorted(os.listdir(folder_path), alg=ns.IC)
        num_videos = len(file_names)
        print(f"    [INFO]\t\tFound {num_videos} videos.")
        for video_idx, video_name in enumerate(file_names):
            print(f"    [INFO]\t\t({video_idx + 1}/{num_videos})\tProcessing video \"{video_name}\"")
            video_path_in = os.path.join(folder_path, video_name)
            video_path_out = os.path.join(new_videos_folder_path, video_name)

            # Call the method to pad video frames
            pad_videos(video_path_in, video_path_out, target_frames)

    # ----------------------------------------------------------------------------------------------
    #                           Step 4 : Resize video frames (width, height)
    # ----------------------------------------------------------------------------------------------

    print()
    print(f"    [INFO]\t{'=' * 50}")
    print(f"    [INFO]\t\t\tRESIZING VIDEOS")
    print(f"    [INFO]\t{'=' * 50}")

    # Iterate through all the folders (classes) and process all videos
    for folder_idx, folder_name in enumerate(folder_names):
        print(f"    [INFO]\t({folder_idx + 1}/{num_folders})\tProcessing folder \"{folder_name}\"")

        # Keep `path_in` and `path_out` the same directory to overwrite the existing
        # files with the resized versions
        folder_path = os.path.join(padded_videos_directory, folder_name)
        resized_videos_folder_path = os.path.join(padded_videos_directory, folder_name)

        # Get all videos inside each class folder
        file_names = natsorted(os.listdir(folder_path), alg=ns.IC)
        num_videos = len(file_names)
        print(f"    [INFO]\t\tFound {num_videos} videos.")
        for video_idx, video_name in enumerate(file_names):
            print(f"    [INFO]\t\t({video_idx + 1}/{num_videos})\tProcessing video \"{video_name}\"")
            video_path_in = os.path.join(folder_path, video_name)
            video_path_out = os.path.join(resized_videos_folder_path, f'temp_{video_name}')

            # Call method to resize each video
            resize_videos(video_path_in, video_path_out, new_dims)

            # Overwrite the existing video
            os.remove(video_path_in)
            os.rename(video_path_out, video_path_in)

    # ----------------------------------------------------------------------------------------------
    #                           Step 5 : Perform Video Data Augmentation
    # ----------------------------------------------------------------------------------------------

    print()
    print(f"    [INFO]\t{'=' * 50}")
    print(f"    [INFO]\t\t\tDATA AUGMENTATION")
    print(f"    [INFO]\t{'=' * 50}")

    # Iterate through all the folders (classes) and process all videos
    for folder_idx, folder_name in enumerate(folder_names):
        print(f"    [INFO]\t({folder_idx + 1}/{num_folders})\tProcessing folder \"{folder_name}\"")
        folder_path = os.path.join(padded_videos_directory, folder_name)
        augmented_videos_folder_path = os.path.join(augmented_dataset_path, folder_name)
        os.makedirs(augmented_videos_folder_path, exist_ok=True)

        # Get all videos inside each class folder
        file_names = natsorted(os.listdir(folder_path), alg=ns.IC)
        num_videos = len(file_names)
        print(f"    [INFO]\t\tFound {num_videos} videos.")

        for video_idx, video_name in enumerate(file_names):
            print(f"    [INFO]\t\t({video_idx + 1}/{num_videos})\tProcessing video \"{video_name}\"")
            video_path_in = os.path.join(folder_path, video_name)
            shutil.copy(video_path_in, augmented_videos_folder_path)
            for augmentation in augmentation_methods:
                method = AUGMENTATION_METHODS.get(augmentation)
                augmented_video_name = f"{video_name.split('.')[0]}_{method}{VIDEO_EXT}"
                video_path_out = os.path.join(augmented_videos_folder_path, augmented_video_name)
                augment_dataset(video_path_in, video_path_out, method)

    # ----------------------------------------------------------------------------------------------
    #                           Step 6 : Convert videos to frames
    # ----------------------------------------------------------------------------------------------

    print()
    print(f"    [INFO]\t{'=' * 50}")
    print(f"    [INFO]\t\t\tCONVERTING VIDEOS TO IMAGES")
    print(f"    [INFO]\t{'=' * 50}")

    padded_frames_directory = os.path.join(path_out, 'frames_dir')
    os.makedirs(padded_frames_directory, exist_ok=True)

    # Iterate through all the folders (classes) and process all videos
    for folder_idx, folder_name in enumerate(folder_names):
        print(f"    [INFO]\t({folder_idx + 1}/{num_folders})\tProcessing folder \"{folder_name}\"")
        folder_path = os.path.join(augmented_dataset_path, folder_name)
        new_frames_folder_path = os.path.join(padded_frames_directory, folder_name)
        os.makedirs(new_frames_folder_path, exist_ok=True)

        # Get all videos inside each class folder
        file_names = natsorted(os.listdir(folder_path), alg=ns.IC)
        num_videos = len(file_names)
        print(f"    [INFO]\t\tFound {num_videos} videos.")
        for video_idx, video_name in enumerate(file_names):
            print(f"    [INFO]\t\t({video_idx + 1}/{num_videos})\tProcessing video \"{video_name}\"")
            video_path_in = os.path.join(folder_path, video_name)
            frames_path_out = os.path.join(new_frames_folder_path, video_name.split('.')[0])
            os.makedirs(frames_path_out, exist_ok=True)

            # Call the method to convert video to frames
            video2images(video_path_in, frames_path_out)

    # ----------------------------------------------------------------------------------------------
    #                           Step 7 : Prepare test-videos directory
    # ----------------------------------------------------------------------------------------------

    # Iterate through all class folders
    for class_name in os.listdir(padded_videos_directory):
        class_path = os.path.join(padded_videos_directory, class_name)
        new_class_path = os.path.join(test_videos_dir, class_name)
        os.makedirs(new_class_path, exist_ok=True)

        # Get all videos in directory and randomly shuffle them
        all_videos = natsorted(os.listdir(class_path), alg=ns.IC)
        np.random.shuffle(all_videos)
        # Select the first `n` videos for testing
        video_names = all_videos[:num_test_videos_per_class]

        # Copy the selected `n` videos from original dataset to test-videos directory
        for video in video_names:
            path_in = os.path.join(class_path, video)
            path_out = os.path.join(new_class_path, video)
            shutil.copy(path_in, path_out)

    print(f"\n    [INFO]\tDone!")


if __name__ == "__main__":
    main()
