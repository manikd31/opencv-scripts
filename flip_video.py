"""
Helper script to process videos inside a folder and flip them horizontally to double the size of the data-set.

Usage:
    flip_video.py (-h | --help)
"""

import ffmpeg
import os
import cv2
from PyInquirer import prompt

TEST_PATH_IN = r"C:/Users/Manik/Desktop/test_CV_videos"
TEST_PATH_OUT = TEST_PATH_IN
VIDEO_EXT = ".mp4"
FOURCC = 0x7634706d


def flip():
    print()


def main():
    answer_videos_dir = prompt({
        'type': 'input',
        'name': 'videos_dir',
        'message': 'Enter the path to the videos directory: ',
        'default': TEST_PATH_IN
    })
    videos_dir = answer_videos_dir['videos_dir']

    answer_save_dir = prompt({
        'type': 'input',
        'name': 'save_dir',
        'message': 'Enter the path to the directory to save flipped videos: ',
        'default': TEST_PATH_OUT
    })
    save_dir = answer_save_dir['save_dir']

    answer_flip_method = prompt({
        'type': 'list',
        'name': 'flip_method',
        'message': 'Select flipping method:',
        'choices': [
            'OpenCV',
            'FFMPEG'
        ]
    })
    flip_method = answer_flip_method['flip_method']

    num_videos = len(os.listdir(videos_dir))
    print(f"    [INFO]\tFound {num_videos} videos.")
    for _id, video in enumerate(os.listdir(videos_dir)):
        print(f"    [INFO]\t({_id + 1}/{num_videos})  Processing video \"{video}\"")
        video_path = os.path.join(videos_dir, video)
        flipped_name = f"{video.split('.')[0]}_flipped{VIDEO_EXT}"
        save_path = os.path.join(save_dir, flipped_name)

        if flip_method.lower() == 'opencv':
            # OpenCV version -- fast
            cap = cv2.VideoCapture(video_path)
            out = cv2.VideoWriter(save_path, FOURCC, cap.get(5), (int(cap.get(3)), int(cap.get(4))))
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.flip(frame, 1)
                out.write(frame)
            cap.release()
            out.release()
        else:
            # FFMPEG version -- slow
            flipped_video = ffmpeg.hflip(ffmpeg.input(video_path))
            out = ffmpeg.output(flipped_video, filename=save_path)
            ffmpeg.run(out, quiet=True)

    print("    [INFO]\tDone!")


if __name__ == "__main__":
    main()