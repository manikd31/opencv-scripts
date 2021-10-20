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
from natsort import natsorted
from natsort import ns

FRAMES = 40


def video2images(path_in, path_out):
    """Convert video to frames and save as .jpg images"""
    cap = cv2.VideoCapture(path_in)
    num_frames = cap.get(7)
    fps = cap.get(5)
    print(f"Number of frames (cap.get()) = {num_frames} recorded at fps = {fps}")
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
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


def pad_videos(path_in, path_out):
    """Add or remove frames for constant video length"""
    cap = cv2.VideoCapture(path_in)
    fps = cap.get(5)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    frames = np.array(frames)
    num_frames = len(frames)
    diff = num_frames - FRAMES
    print(f"\nDIFF = {diff}\n")
    print(f"Original slice ranges = (0, {num_frames - 1})\n")

    new_frames = frames
    if diff == 0:
        print("Good to go!")
    else:
        if diff > 0:
            if diff % 2 == 0:
                new_start_idx = diff // 2
                new_end_idx = num_frames - diff // 2
            else:
                new_start_idx = diff // 2 + 1
                new_end_idx = num_frames - diff // 2
            print(f"New slice ranges = [{new_start_idx}, {new_end_idx})")

            new_frames = frames[new_start_idx:new_end_idx]

            print(f"\nFinal frames list = {len(new_frames)} frames")

        else:
            diff = abs(diff)
            if diff % 2 == 0:
                pad_to_start = diff // 2
                pad_to_end = diff - diff // 2
            else:
                pad_to_start = diff // 2
                pad_to_end = diff - diff // 2
            print(f"pad-start = {pad_to_start}, pad-end = {pad_to_end}")
            new_end_idx = num_frames + pad_to_start + pad_to_end
            print(f"New slice ranges = [0, {new_end_idx})")

            new_frames = []
            for start in range(pad_to_start):
                new_frames.append(frames[0])
            for frame in frames:
                new_frames.append(frame)
            for end in range(pad_to_end):
                new_frames.append(frames[-1])
            new_frames = np.array(new_frames)
            print(f"\nFinal frames list = {len(new_frames)} frames")

    print(f"\nType = {type(new_frames)}, length = {len(new_frames)}")

    for frame_id, frame in enumerate(new_frames):
        img = Image.fromarray(frame)
        img.save(os.path.join(path_out, f"{frame_id}.jpg"))

    vid_name = os.path.join(path_out, 'video.mp4')
    images2video(path_out, vid_name, fps)


def main():
    """Main body"""
    # path_in = r"C:/Users/Manik/Desktop/test_videos/wave/user01_0_downsized_at_fps=8.mp4"
    path_in = r"C:/Users/Manik/Desktop/Hand-Gestures-Videos/wave/user01_0.mp4"
    path_out = r"C:/Users/Manik/Desktop/test_videos/video"
    os.makedirs(path_out, exist_ok=True)
    # video2images(path_in, path_out)
    pad_videos(path_in, path_out)
    print("Done!")


if __name__ == "__main__":
    main()