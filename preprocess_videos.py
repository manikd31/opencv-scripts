"""
Script to preprocess video.

Usage:
    preprocess_video.py (-h | --help)
"""

# ===================================================================================================
# This will be a helped file which will be responsible for:
#   - add padding (duplicate frames for short videos) or remove frames (for long videos)
#   - resize videos to a desired shape (Width, Height, Channels)
#   - the final video dataset should contain:
#       - equal number of frames throughout
#       - shape as desired by the model
#       - dataset folder of the specified convention
# ===================================================================================================
# Should follow a pattern and process all videos in the dataset and ready
# the data to be used by the model for training.
#   (1)     get all raw videos from the dataset folder
#   (2)     downsize all videos to 8 or 12 fps and create a new folder of videos
#   (3)     perform data augmentation on these downsized videos
#   (4)     (OPTIONAL) create 3 channels for only grayscale videos since they might be
#           single channel after conversion to grayscale
#   (5)     resize videos to the given input shape for the model
#   (6)     pad or remove frames to make video size consistent
#   (7)     figure out what to do about video-to-images and how to use videos for training on batches
#
#   (8)     finally, return the new dataset folder, keeping the raw videos unchanged
#           in the original folder
# ===================================================================================================
#       /path-to-the-dataset/
#       |--- videos_train
#       |   |--- class_1
#       |   |   |--- video_1.mp4
#       |   |   |--- video_2.mp4
#       |   |   |--- ...
#       |   |--- class_2
#       |   |   |--- video_1.mp4
#       |   |   |--- video_2.mp4
#       |   |   |--- ...
#       |   |--- ...
#       |--- videos_valid
#       |   |--- class_1
#       |   |   |--- video_3.mp4
#       |   |   |--- video_4.mp4
#       |   |   |--- ...
#       |   |--- class_2
#       |   |   |--- video_3.mp4
#       |   |   |--- video_4.mp4
#       |   |   |--- ...
#       |   |--- ...
#        -----------------------
# ===================================================================================================

import cv2
import numpy as np
import os
from PIL import Image
from constants import FOURCC
from constants import TEST_PATH_IN
from constants import TEST_PATH_OUT
from constants import PROP_ID_FPS
from constants import PROP_ID_WIDTH
from constants import PROP_ID_HEIGHT
from natsort import natsorted
from natsort import ns
from PyInquirer import prompt


def resize_videos(path_in, path_out, resize_dims):
    """Resize the current video and overwrite with the resized size video"""
    cap = cv2.VideoCapture(path_in)
    out = cv2.VideoWriter(path_out, FOURCC, cap.get(PROP_ID_FPS), resize_dims)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()

    for frame in frames:
        frame = np.array(Image.fromarray(frame).resize(resize_dims))
        out.write(frame)
    out.release()


def video2images(path_in, path_out):
    """Convert video to frames and save as .jpg images"""
    cap = cv2.VideoCapture(path_in)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = np.flip(frame, axis=-1)
        frames.append(frame)
    cap.release()

    for _id, img in enumerate(frames):
        img = Image.fromarray(img)
        img.save(os.path.join(path_out, f"{_id}.jpg"))


def images2video(path_in, path_out, fps):
    """Convert frames to video and save as .mp4"""
    frames = natsorted(os.listdir(path_in), alg=ns.IC)
    print(frames)
    img = Image.open(os.path.join(path_in, frames[0]))
    out = cv2.VideoWriter(path_out, FOURCC, fps, img.size)
    for frame in frames:
        img = np.array(Image.open(os.path.join(path_in, frame)))
        out.write(img)
    out.release()


def pad_videos(video_path_in, video_path_out, target_frames):
    """Add or remove frames for constant video length"""
    cap = cv2.VideoCapture(video_path_in)
    out = cv2.VideoWriter(video_path_out, FOURCC, cap.get(PROP_ID_FPS),
                          (int(cap.get(PROP_ID_WIDTH)), int(cap.get(PROP_ID_HEIGHT))))

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()

    frames = np.array(frames)
    num_frames = len(frames)
    diff = int(num_frames - target_frames)

    new_frames = frames
    if diff == 0:
        pass
    else:
        if diff > 0:
            if diff % 2 == 0:
                new_start_idx = diff // 2
                new_end_idx = num_frames - diff // 2
            else:
                new_start_idx = diff // 2 + 1
                new_end_idx = num_frames - diff // 2
            new_frames = frames[new_start_idx:new_end_idx]

        else:
            diff = abs(diff)
            if diff % 2 == 0:
                pad_to_start = diff // 2
                pad_to_end = diff - diff // 2
            else:
                pad_to_start = diff // 2
                pad_to_end = diff - diff // 2

            new_frames = []
            for start in range(pad_to_start):
                new_frames.append(frames[0])
            for frame in frames:
                new_frames.append(frame)
            for end in range(pad_to_end):
                new_frames.append(frames[-1])
            new_frames = np.array(new_frames)

    for frame_idx, frame in enumerate(new_frames):
        out.write(frame)
    out.release()


def main():
    """Main body"""

    target_frames = 40

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

    answer_save_frames = prompt({
        'type': 'list',
        'name': 'save_frames',
        'message': 'Do you want to save the padded videos as frames?',
        'choices': [
            'Yes',
            'No'
        ]
    })
    save_frames = answer_save_frames['save_frames'] == 'Yes'

    os.makedirs(path_out, exist_ok=True)

    num_folders = len(folder_names)
    print(f"    [INFO]\tFound {num_folders} folders.")
    for folder_id, folder in enumerate(folder_names):
        print(f"    [INFO]\t({folder_id + 1}/{num_folders})\tProcessing folder \"{folder}\"")
        folder_path = os.path.join(path_in, folder)
        new_folder_path = os.path.join(path_out, folder)
        os.makedirs(new_folder_path, exist_ok=True)

        file_names = os.listdir(folder_path)
        if not is_dataset:
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
                    'message': 'Select the videos to blur: ',
                    'choices': [{'name': _file} for _file in os.listdir(folder_path)]
                })
                file_names = answer_file_names['file_names']

        num_videos = len(file_names)
        print(f"    [INFO]\t\tFound {num_videos} videos.")
        for video_id, video in enumerate(file_names):
            print(f"    [INFO]\t\t({video_id + 1}/{num_videos})\tProcessing video \"{video}\"")
            video_path = os.path.join(folder_path, video)
            save_path = os.path.join(new_folder_path, video)
            pad_videos(video_path, save_path, target_frames)
            if save_frames:
                frames_path = os.path.join(new_folder_path, 'frames', video.split('.')[0])
                os.makedirs(frames_path, exist_ok=True)
                video2images(save_path, frames_path)

    print("    [INFO]\tDone!")


if __name__ == "__main__":
    main()
