import cv2
import numpy as np
import keras
import os
from threading import Thread
import queue
# import multiprocessing

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
# que = multiprocessing.Manager().Queue()


# def worker(que):
#     # frames = np.expand_dims(frames, axis=0)
#     # predictions = np.argmax(model.predict(frames), axis=1)[0]
#     predictions = 0
#     que.put(predictions)

# class Worker(multiprocessing.Process):
#     def __init__(self,que):
#         # super().__init__(self)
#         self.model = keras.models.load_model(weights_path)
#         self.que = que
#
#
#     def run(self,frames):
#         frames = np.expand_dims(frames, axis=0)
#         predictions = np.argmax(self.model.predict(frames), axis=1)[0]
#         # predictions = 0
#         self.que.put(predictions)
#         return


class Inference(Thread):
    def __init__(self, model):
        Thread.__init__(self)
        self.model = model
        print(self.model.summary())
        self.shutdown = False
        self.queue_in = queue.Queue(20)
        self.queue_out = queue.Queue(1)

        init_frames = np.random.random((20, 100, 100, 3))
        for frame in init_frames:
            self.queue_in.put_nowait(frame)

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
                frames = np.array(self.queue_in.queue)
                frames = np.expand_dims(frames, axis=0)
            except queue.Empty:
                frames = None

            if frames is not None:
                predictions = self.infer(frames)
                del frames
                predictions = predictions[0]

                if self.queue_out.full():
                    # Remove one frame
                    self.queue_out.get_nowait()
                    print("*** Unused predictions ***")
                self.queue_out.put(predictions, block=False)

    def infer(self, clip):
        frames = clip
        predictions = self.model.predict(frames)
        predictions = np.argmax(predictions, axis=1)

        return predictions


def main():
    """Main body"""
    for c_idx, c_name in enumerate(class_names):
        INT2LAB[c_idx] = c_name
        LAB2INT[c_name] = c_idx

    model = keras.models.load_model(weights_path)
    # pool = multiprocessing.Pool(processes=4,initializer=Worker, initargs=(que, ))

    cap = cv2.VideoCapture(0)

    inference = Inference(model)
    inference.start()

    frame_idx = 0
    step_size = 16
    predictions = 0
    while True:
        ret, frame = cap.read()
        frame_idx += 1
        frame = cv2.flip(frame, 1)
        frame_copy = frame.copy()
        if not ret:
            cv2.destroyAllWindows()
            break
        # frame = (100, 100, 3) --> (1, 100, 100, 3)
        frame = cv2.resize(frame, (100, 100))

        inference.put_nowait(frame)
        if frame_idx % step_size == 0:
            predictions = inference.get_nowait()

        # frames.append(frame)
        # if len(frames) == 20:
            # frames = (20, 100, 100, 3) --> (1, 20, 100, 100, 3)
            # p = Worker()
            # pool.apply(frames)
            # frames = []

        # if not que.empty():
        #     predictions = que.get()

        cv2.putText(frame_copy, f"Predicted : {INT2LAB[predictions]}", (20, 20), FONT_STYLE, 1.5, (255, 255, 255), 2)
        cv2.imshow("Frame", frame_copy)

        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break

    inference.stop()


if __name__ == "__main__":
    main()
