"""
Script to downsize a video, i.e. reduce the fps of any video with given fps value.

Usage:
    downsize_video.py [--path_in=PATH_IN]
                      [--path_out=PATH_OUT]
                      [--file_name=FILE_NAME]
                      [--target_fps=TARGET_FPS]
                      [--is_dir]
    downsize_video.py (-h | --help)

Options:
    --path_in=PATH_IN           Path to the folder containing the video file
    --path_out=PATH_OUT         Path to save the downsized video file
    --file_name=FILE_NAME       Name of the video (with extension)
    --target_fps=TARGET_FPS     Target FPS
    --is_dir                    Boolean to indicate if the path is for video or complete dataset
"""

import os
import cv2
from docopt import docopt

TEST_PATH_IN = r"C:/Users/Manik/Desktop/test_CV_videos"
TEST_PATH_OUT = TEST_PATH_IN
TEST_FILE_NAME = "test_video0.mp4"
TEST_TARGET_FPS = 4.0

ID_WIDTH = 3
ID_HEIGHT = 4
ID_FPS = 5
ID_FRAME_COUNT = 7

FOURCC = 0x7634706d


def parse_video(cap, path_out, file_name, target_fps):
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
    name, ext = file_name.split('.')
    new_file_name = f"{name}_downsized_at_fps={int(target_fps)}.{ext}"

    width = int(cap.get(ID_WIDTH))
    height = int(cap.get(ID_HEIGHT))
    current_fps = int(cap.get(ID_FPS))
    frame_count = int(cap.get(ID_FRAME_COUNT))
    # frame_jump = int(current_fps / target_fps)
    frame_jump = current_fps / target_fps  # Use this for trying method-2

    out = cv2.VideoWriter(os.path.join(path_out, new_file_name), FOURCC, target_fps, (width, height))

    curr_frame = 0
    prev_frame_idx = -1
    while curr_frame < frame_count:
        new_frame_idx = int(i * frame_jump)
        if new_frame_idx != prev_frame_idx:
            cap.set(1, new_frame_idx)
            _, frame = cap.read()
            out.write(frame)
            prev_frame_idx = new_frame_idx
        curr_frame += 1

    out.release()


def main():
    """Main body of the script to be run."""

    # Parse arguments
    args = docopt(__doc__)
    path_in = args["--path_in"] or TEST_PATH_IN
    path_out = args["--path_out"] or TEST_PATH_OUT
    file_name = args["--file_name"] or TEST_FILE_NAME
    target_fps = float(args["--target_fps"]) if args["--target_fps"] else TEST_TARGET_FPS
    is_dir = args["--is_dir"] or False

    if not os.path.isdir(path_in):
        print(f"    [ERROR]\tThe folder \"{path_in}\" doesn't exist.")
    elif not os.path.isfile(os.path.join(path_in, file_name)):
        print(f"    [ERROR]\tThe file \"{file_name}\" or folder \"{path_in}\" doesn't exist.")
    else:
        if is_dir:
            all_videos = os.listdir(path_in)
            num_videos = len(all_videos)
            print(f"    [INFO]\tFound {num_videos} videos.")
            for _id, video in enumerate(all_videos):
                video_path = os.path.join(path_in, video)
                capture = cv2.VideoCapture(video_path)
                message = ""
                if target_fps >= capture.get(ID_FPS):
                    print(f"    [INFO]\tTarget FPS is equal to or larger than source FPS, skipping video {_id + 1}.")
                else:
                    os.makedirs(path_out, exist_ok=True)
                    parse_video(capture, path_out, video, target_fps)
                    print(f"    [INFO]\tProcessed {_id + 1} / {num_videos} videos.")
                capture.release()
            print("    [INFO]\tDone!")
        else:
            video_path = os.path.join(path_in, file_name)
            capture = cv2.VideoCapture(video_path)
            if target_fps >= capture.get(ID_FPS):
                print(f"    [INFO]\tTarget FPS is equal to or larger than source FPS, skipping video.")
            else:
                parse_video(capture, path_out, file_name, target_fps)
                print("    [INFO]\tDone!")
            capture.release()


if __name__ == "__main__":
    main()
