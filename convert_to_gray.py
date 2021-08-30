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

    answer_videos_dir = prompt({
        'type': 'input',
        'name': 'videos_dir',
        'message': 'Enter the path to the videos directory: ',
        'default': TEST_PATH_IN
    })
    videos_dir = answer_videos_dir['videos_dir']
    if not os.path.isdir(videos_dir):
        print(f"    [ERROR]\tThe folder \"{videos_dir}\" doesn't exist.")
        return

    answer_save_dir = prompt({
        'type': 'input',
        'name': 'save_dir',
        'message': 'Enter the path to save the converted videos to: ',
        'default': TEST_PATH_OUT
    })
    save_dir = answer_save_dir['save_dir']
    os.makedirs(save_dir, exist_ok=True)

    num_videos = len(os.listdir(videos_dir))
    print(f"    [INFO]\tFound {num_videos} videos.")
    for _id, video in enumerate(os.listdir(videos_dir)):
        print(f"    [INFO]\t({_id + 1}/{num_videos})  Processing video \"{video}\"")
        video_path = os.path.join(videos_dir, video)
        grayscale_video_name = f"{video.split('.')[0]}_grayscale{VIDEO_EXT}"
        save_path = os.path.join(save_dir, grayscale_video_name)
        convert_to_gray(video_path, save_path)

    print("    [INFO]\tDone!")


if __name__ == "__main__":
    main()
