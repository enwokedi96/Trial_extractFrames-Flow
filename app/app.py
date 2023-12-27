from flask import Flask, render_template, request, jsonify, redirect, url_for
import cv2
import os, glob, shutil
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

UPLOAD_FOLDER = app.config["UPLOAD_FOLDER"]
STATIC_FOLDER = app.config["STATIC_FOLDER"]
ALLOWED_EXTENSIONS = app.config["ALLOWED_EXTENSIONS"]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract_frames', methods=['POST'])
def extract_frames(frame_skips = 5):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        video_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(video_path)

        frames_folder = os.path.join(STATIC_FOLDER, 'frames')
        os.makedirs(frames_folder, exist_ok=True)

        # wipe memory of frames folder
        if os.listdir(frames_folder) != []:
            for i in os.listdir(frames_folder):
                os.remove(os.path.join(frames_folder, i))
            
        # Use OpenCV to capture frames from the video
        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # skip all frames that do not lie as 
            # multiples of the set 'frame_skips'
            if frame_count % frame_skips != 0: 
                frame_count += 1
                continue
            
            frame_filename = os.path.join(frames_folder, f'frame_{frame_count}.jpg')
            cv2.imwrite(frame_filename, frame)
            frame_count += 1
            # print(frame_filename)

        cap.release()

        # return jsonify({'message': 'Frames extracted successfully', 'frame_count': frame_count})

        # getting all the files in the source directory
        files = os.listdir(frames_folder)

        # wipe memory of frames folder
        if os.listdir(UPLOAD_FOLDER+"/frames") != []:
            for i in os.listdir(UPLOAD_FOLDER+"/frames"):
                os.remove(os.path.join(UPLOAD_FOLDER+"/frames", i))
        
        # copy to new folder (from static to upload)
        for i in files:
            shutil.copy2(os.path.join(STATIC_FOLDER+"/frames",i), UPLOAD_FOLDER+"/frames")

        # Redirect to the thumbnails page after extracting frames
        return redirect(url_for('thumbnails'))

    return jsonify({'error': 'Invalid file format'})

@app.route('/thumbnails')
def thumbnails():
    frames_folder = os.path.join(STATIC_FOLDER, 'frames')
    
    # for jpgfile in glob.iglob(os.path.join(frames_src_folder, "*.jpg"))[:50]:
    #     shutil.copy(jpgfile, frames_dest_folder)
    
    frame_files = sorted([f for f in os.listdir(frames_folder) if f.endswith('.jpg')])[:100]
    thumbnails = [{'filename': f, 'path': f} for f in sorted(frame_files)]

    return render_template('thumbnails.html', thumbnails=thumbnails)

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], host='0.0.0.0', port=80)
