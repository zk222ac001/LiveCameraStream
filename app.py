from flask import Flask, Response, render_template, jsonify
from picamera_stream import PiCameraStream
import psutil
import time

app = Flask(__name__)

# Initialize PiCamera stream
camera = PiCameraStream(resolution=(640, 480), framerate=24)

# FPS calculation variables
last_time = time.time()
frame_count = 0
fps = 0

def gen_frames():
    """Generator that yields camera frames as MJPEG stream"""
    global frame_count, fps, last_time
    while True:
        frame = camera.get_frame()
        if frame is not None:
            frame_count += 1
            # Update FPS every second
            current_time = time.time()
            if current_time - last_time >= 1:
                fps = frame_count
                frame_count = 0
                last_time = current_time
            # Yield frame in proper MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in an <img> tag in HTML."""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def stats():
    """Return system stats as JSON."""
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    return jsonify({'cpu': cpu, 'memory': mem, 'fps': fps})

@app.route('/')
def index():
    """Render dashboard HTML page."""
    return render_template('dashboard.html')

if __name__ == '__main__':
    try:
        # Run Flask app on all interfaces
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        # Stop camera cleanly on exit
        camera.stop()
