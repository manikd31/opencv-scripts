"""
Script to blur the video to some extent.

Usage:
    blue_video.py (-h | --help)
"""

from PyInquirer import prompt
import cv2
import os

from constants import BLUR_INTENSITY
from constants import FOURCC
from constants import PROP_ID_FPS
from constants import PROP_ID_HEIGHT
from constants import PROP_ID_WIDTH
from constants import TEST_PATH_IN
from constants import TEST_PATH_OUT
from constants import VIDEO_EXT

KERNEL_SIZE = BLUR_INTENSITY.get("MEDIUM")


def blur_video(path_in: str,
               path_out: str):
    """
    Method to convert given source video from COLOR to GRAYSCALE and save at destination.

    :param path_in:
        Path to the video file to invert colors for
    :param path_out:
        Path to save the converted video
    """

    cap = cv2.VideoCapture(path_in)
    out = cv2.VideoWriter(path_out, FOURCC, cap.get(PROP_ID_FPS),
                          (int(cap.get(PROP_ID_WIDTH)), int(cap.get(PROP_ID_HEIGHT))))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.blur(frame, KERNEL_SIZE)
        out.write(frame)

    cap.release()
    out.release()


def main():
    """Main body of the script to be run."""

    global KERNEL_SIZE

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

    answer_blur_intensity = prompt({
        'type': 'list',
        'name': 'blur_intensity',
        'message': 'Select the intensity of blur to add to the video(s).',
        'choices': BLUR_INTENSITY.keys()
    })
    blur_intensity = answer_blur_intensity['blur_intensity']
    KERNEL_SIZE = BLUR_INTENSITY.get(blur_intensity)

    os.makedirs(path_out, exist_ok=True)
    num_videos = len(file_names)
    print(f"    [INFO]\tFound {num_videos} videos.")
    for _id, video in enumerate(file_names):
        print(f"    [INFO]\t({_id + 1}/{num_videos})  Processing video \"{video}\"")
        video_path = os.path.join(path_in, video)
        blurred_video_name = f"{video.split('.')[0]}_blur={blur_intensity}{VIDEO_EXT}"
        save_path = os.path.join(path_out, blurred_video_name)
        blur_video(video_path, save_path)

    print("    [INFO]\tDone!")


if __name__ == "__main__":
    main()
