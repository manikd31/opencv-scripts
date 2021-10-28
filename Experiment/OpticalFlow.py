import pickle
import csv
import cv2
import numpy as np
from pathlib import Path

video_file = "./user02_0.mp4"

class_idx = {"background": 1, "clap": 2, "peace": 3, "swipe_left": 4, "swipe_right": 5, "thumbs_down": 6, "thumbs_up": 7, "wave": 8 }



def preprocess(vid_path):

    # Get a VideoCapture object from video and store it in vs
    vc = cv2.VideoCapture(vid_path)
    # Read first frame
    ret, first_frame = vc.read()
    # Scale and resize image
    max_dim = max(first_frame.shape)
    resize_dim = 342 #256
    scale = resize_dim/max_dim

    first_frame = cv2.resize(first_frame, None, fx=scale, fy=scale)
    h, w, c = first_frame.shape
    # Convert to gray scale
    prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)


    # Create mask
    mask = np.zeros_like(first_frame)
    # Sets image saturation to maximum
    mask[..., 1] = 255


    #Optical flow bounding. [-bound, bound] will be mapped to [0, 255].
    bound = 15


    # visualize flow frames
    visualize = False

    x_channel = []
    y_channel = []
    frames = []

    out = cv2.VideoWriter('video.mp4',-1,1,(600, 600))

    optical_flow = cv2.optflow.createOptFlow_DualTVL1()
    while(vc.isOpened()):
        # Read a frame from video
        ret, frame = vc.read()
        
        if frame is None:
            print("END")
            break
        # Convert new frame format`s to gray scale and resize gray frame obtained
        f = cv2.resize(frame, None, fx=scale, fy=scale)
        frames.append(f)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=scale, fy=scale)

        # Calculate dense optical flow by Farneback method
        # https://docs.opencv.org/3.0-beta/modules/video/doc/motion_analysis_and_object_tracking.html#calcopticalflowfarneback
        # flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, pyr_scale = 0.5, levels = 5, winsize = 11, iterations = 5, poly_n = 5, poly_sigma = 1.1, flags = 0)


        # calculate optical flow TVL1
        # optical_flow = cv2.optflow.DualTVL1OpticalFlow_create()
        flow = optical_flow.calc(prev_gray, gray, None)
        #[-1,1] -> [0,255]


        # map optical flow back
        flow = flow / scale
        # normalization
        flow = np.round((flow + bound) / (2. * bound) * 255.)
        flow[flow < 0] = 0
        flow[flow > 255] = 255
        flow = cv2.resize(flow, (w, h))



        # print("Optical flow: ", flow.shape)
        x_channel.append(flow[...,0].squeeze())
        y_channel.append(flow[...,1].squeeze())

        # Update previous frame
        prev_gray = gray

        if visualize:
            # Compute the magnitude and angle of the 2D vectors
            magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            # Set image hue according to the optical flow direction
            mask[..., 0] = angle * 180 / np.pi / 2
            # Set image value according to the optical flow magnitude (normalized)
            mask[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
            # Convert HSV to RGB (BGR) color representation
            rgb = cv2.cvtColor(mask, cv2.COLOR_HSV2BGR)
            
            # Resize frame size to match dimensions
            frame = cv2.resize(frame, None, fx=scale, fy=scale)
            
            # Open a new window and displays the output frame
            dense_flow = cv2.addWeighted(frame, 1,rgb, 2, 0)
            cv2.imshow("Dense optical flow", dense_flow)
            out.write(dense_flow)
        # Frame are read by intervals of 1 millisecond. The programs breaks out of the while loop when the user presses the 'q' key
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    # The following frees up resources and closes all windows
    vc.release()
    cv2.destroyAllWindows()
    # intervals = np.linspace(0, len(x_channel), CHANNELS, endpoint=False, dtype=int)
    # x_stack = np.stack(x_channel,-1)[:,:,intervals]
    # y_stack = np.stack(y_channel,-1)[:,:,intervals]

    vid_name = Path(vid_path)
    p1 = Path("datasets/rgb_frames") / vid_name.stem
    p2 = Path("datasets/flow_frames") / vid_name.stem / "x"
    p3 = Path("datasets/flow_frames") / vid_name.stem / "y"

    p1.mkdir(parents=True, exist_ok=True)
    p2.mkdir(parents=True, exist_ok=True)
    p3.mkdir(parents=True, exist_ok=True)

    for i, img in enumerate(frames):
        cv2.imwrite(str(p1 / f'frame{i+1:06d}.jpg'), img)

    for i, img in enumerate(x_channel):
        cv2.imwrite(str(p2 / f'frame{i+1:06d}.jpg'), x_channel[i])
    for i, img in enumerate(y_channel):
        cv2.imwrite(str(p3 / f'frame{i+1:06d}.jpg'), y_channel[i])
    return len(frames)


if __name__ == "__main__":
    csv_file = []
    all_dir = Path("./Hand-Gestures-Videos/Hand-Gestures-Videos/mp4/data")
    for folder in all_dir.iterdir():
        for file_name in folder.iterdir():
            num_frames = preprocess(str(file_name))
            csv_file.append((str(file_name.stem), str(num_frames), str(class_idx[str(folder.name)])))


    #pickle.dump(csv_file, open("csv_data.bin","wb"))
    with open("train.txt", "w") as ft:
        file_writer = csv.writer(ft,delimiter=' ', quotechar=',', quoting=csv.QUOTE_MINIMAL)
        for line in csv_file:
            file_writer.writerow(line)

