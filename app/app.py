from flask import Flask, render_template, request, jsonify
import cv2
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

UPLOAD_FOLDER = app.config["UPLOAD_FOLDER"]
ALLOWED_EXTENSIONS = app.config["ALLOWED_EXTENSIONS"]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract_frames', methods=['POST'])
def extract_frames():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        video_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(video_path)

        frames_folder = os.path.join(UPLOAD_FOLDER, 'frames')
        os.makedirs(frames_folder, exist_ok=True)

        # Use OpenCV to capture frames from the video
        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_filename = os.path.join(frames_folder, f'frame_{frame_count}.jpg')
            cv2.imwrite(frame_filename, frame)
            frame_count += 1

        cap.release()

        return jsonify({'message': 'Frames extracted successfully', 'frame_count': frame_count})

    return jsonify({'error': 'Invalid file format'})

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], host='0.0.0.0', port=80)
