from picamera2 import Picamera2
import cv2
from threading import Thread
import time

class PiCameraStream:
    def __init__(self, resolution=(640, 480), framerate=24):
        self.picam2 = Picamera2()

        # Create preview configuration
        config = self.picam2.create_preview_configuration(
            main={"size": resolution, "format": "RGB888"}
        )
        self.picam2.configure(config)
        self.picam2.start()

        self.frame = None
        self.stopped = False
        self.framerate = framerate

        # Start capture thread
        self.thread = Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while not self.stopped:
            frame = self.picam2.capture_array()
            # Convert RGB -> BGR for OpenCV
            self.frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            time.sleep(1 / self.framerate)

    def get_frame(self):
        if self.frame is None:
            return None
        _, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg.tobytes()

    def stop(self):
        self.stopped = True
        self.thread.join()
        self.picam2.stop()
