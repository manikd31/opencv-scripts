import time

import cv2
import numpy as np
import keras
from threading import Thread
import queue
import os
from PIL import Image

weights_path = r"E:/LakeheadU/Hand-Gestures-Videos/sample_data/base_model.h5"
FONT_STYLE = cv2.FONT_HERSHEY_PLAIN

class_names = [
    'background',
    'clap',
    'peace',
    'swipe_left',
    'swipe_right',
    'thumbs_down',
    'thumbs_up',
    'wave'
]

INT2LAB = dict()
LAB2INT = dict()


class Inference(Thread):
    """
    Thread to get the predictions for a set of 20 frames from the input video stream.
    """

    def __init__(self, model):
        Thread.__init__(self)
        self.model = model
        self.shutdown = False
        self.queue_in = queue.Queue(1)
        self.queue_out = queue.Queue(1)

    def put_nowait(self, frame):
        """
        Add a new clip to the input queue of inference engine for prediction.
        :param frame:
            The video frame to be added to the inference engine's input queue.
        """
        if self.queue_in.full():
            # Remove one clip
            self.queue_in.get_nowait()
        self.queue_in.put_nowait(frame)

    def get_nowait(self):
        """
        Return a clip from the output queue of the inference engine if available.
        """
        if self.queue_out.empty():
            return None
        return self.queue_out.get_nowait()

    def stop(self):
        """Terminate the inference engine."""
        self.shutdown = True

    def run(self):
        """
        Keep the inference engine running and inferring predictions from input video frames.
        """
        while not self.shutdown:
            try:
                frames = self.queue_in.get(timeout=1)
            except queue.Empty:
                frames = None

            if frames is not None:
                predictions = self.infer(frames)
                predictions = predictions[0]

                if self.queue_out.full():
                    # Remove one frame
                    self.queue_out.get_nowait()
                    print("*** Unused predictions ***")
                self.queue_out.put(predictions, False)

    def infer(self, frames):
        predictions = self.model.predict(frames)
        predictions = np.argmax(predictions, axis=1)

        return predictions


class VideoStream(Thread):
    """
    Thread that reads frames from the video source
    """

    def __init__(self, video_source, fps=16, queue_size=20):
        Thread.__init__(self)
        self.video_source = video_source
        self.frames = queue.Queue(queue_size)
        self.fps = fps
        self.delta_t = 1.0 / self.fps
        self.shutdown = False

    def stop(self):
        """Stop the video stream."""
        self.shutdown = True

    def get_image(self):
        """Get the set of frames from the FIFO queue of frames."""
        return self.frames.get()

    def run(self):
        while not self.shutdown:
            start_time = time.perf_counter()
            _, frame = self.video_source.read()

            if frame is None:
                self.stop()
                continue

            if self.frames.full():
                self.frames.get_nowait()
                print("*** Frame skipped ***")
            self.frames.put(frame, False)

            elapsed = time.perf_counter() - start_time
            delay = self.delta_t - elapsed
            if delay > 0:
                time.sleep(delay)


def main():
    """Main body"""
    for c_idx, c_name in enumerate(class_names):
        INT2LAB[c_idx] = c_name
        LAB2INT[c_name] = c_idx

    model = keras.models.load_model(weights_path)
    cap = cv2.VideoCapture(0)

    # initial random frames to get prediction
    frames = np.random.randn(1, 20, 100, 100, 3)

    inference = Inference(model)
    video_stream = VideoStream(video_source=cap)
    inference.start()
    video_stream.start()

    # Current frame index to use while comparing with `step_size`
    frame_idx = 0

    # New clip ready after every `step_size` frames
    step_size = 16

    # Save previous predictions in case new predictions is `None`
    old_predictions = 0

    while True:
        try:
            frame_idx += 1
            frame = video_stream.get_image()

            if frame is None:
                break

            frame = cv2.flip(frame, 1)
            frame_copy = frame.copy()
            frame = cv2.resize(frame, (100, 100))
            frames = np.roll(frames, -1, 1)
            frames[:, -1, :, :, :] = frame

            if frame_idx == step_size:
                # A new clip is ready
                inference.put_nowait(frames)

            frame_idx = frame_idx % step_size

            predictions = inference.get_nowait()
            # predictions = post_process(predictions)

            if predictions is None:
                predictions = old_predictions

            old_predictions = predictions

            cv2.putText(frame_copy, f"Predicted : {INT2LAB[predictions]}",
                        (20, 20), FONT_STYLE, 1.5, (255, 255, 255), 2)
            cv2.imshow("Frame", frame_copy)

            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
                break

        except Exception as e:
            print(f"------ Exception Raised -------\n{e}")
            raise e

    cap.release()
    cv2.destroyAllWindows()
    video_stream.stop()
    inference.stop()


def post_process(predictions):
    predictions = np.argmax(predictions, axis=1)
    return predictions[0]


if __name__ == "__main__":
    main()
    # model = keras.models.load_model(weights_path)
    # video = r"E:/LakeheadU/Hand-Gestures-Videos/sample_data/frames/thumbs_up/video_3"
    # frames = os.listdir(video)
    # all_frames = []
    # for f in frames:
    #     img = Image.open(os.path.join(video, f))
    #     all_frames.append(np.array(img))

    # all_frames = np.random.random((20, 100, 100, 3))
    # _input = np.expand_dims(np.array(all_frames), axis=0)
    # predictions = model.predict(_input)
    # print(predictions)
    # predictions = np.argmax(predictions, axis=1)
    # print(predictions)
