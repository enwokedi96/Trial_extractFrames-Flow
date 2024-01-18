from flask import Flask, render_template, request, jsonify, redirect, url_for
import cv2, natsort
import os, glob, shutil
from config import Config
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
import numpy as np

app = Flask(__name__)
app.config.from_object(Config)

UPLOAD_FOLDER = app.config["UPLOAD_FOLDER"]
STATIC_FOLDER = app.config["STATIC_FOLDER"]
ST_NUMBER = app.config["ST_NUMBER"]
ALLOWED_EXTENSIONS = app.config["ALLOWED_EXTENSIONS"]

# Load the pre-trained MobileNetV2 model
model = MobileNetV2(weights='imagenet')

def prepare_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array

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
        frames_folder_u = os.path.join(UPLOAD_FOLDER, 'frames')
        stClips_folder = os.path.join(UPLOAD_FOLDER, 'stClips')

        # create frames folder in both static and uploads
        if not os.path.exists(frames_folder):
            os.makedirs(frames_folder, exist_ok=True)
        if not os.path.exists(frames_folder_u):
            os.makedirs(frames_folder_u, exist_ok=True)

        # create spatiotemporal folder
        if not os.path.exists(stClips_folder):
            os.makedirs(stClips_folder, exist_ok=True)

        # wipe memory of frames folder
        if os.listdir(frames_folder) != []:
            for i in os.listdir(frames_folder):
                os.remove(os.path.join(frames_folder, i))
            
        # Use OpenCV to capture frames from the video
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        frame_st = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # skip all frames that do not lie as 
            # multiples of the set 'frame_skips'
            if frame_count % frame_skips != 0: 
                frame_count += 1
                continue
            
            frame_st.append(frame)
            # save spatiotemporal clips
            if frame_count>0 and frame_count%ST_NUMBER==0:
                frame_st = np.array(frame_st)
                np.save(os.path.join(stClips_folder,str(frame_count)+".npy"), frame_st)
                frame_st = []
            
            frame_filename = os.path.join(frames_folder, f'frame_{frame_count}.jpg')
            cv2.imwrite(frame_filename, frame)
            frame_count += 1
            # print(frame_filename)

        cap.release()

        # return jsonify({'message': 'Frames extracted successfully', 'frame_count': frame_count})

        # getting all the files in the source directory
        files = os.listdir(frames_folder)

        # wipe memory of upload frames folder
        if os.listdir(frames_folder_u) != []:
            for i in os.listdir(frames_folder_u):
                try:
                    if os.path.isfile(os.path.join(frames_folder_u, i)):
                        os.unlink(os.path.join(frames_folder_u, i))
                    elif os.path.isdir(os.path.join(frames_folder_u, i)):
                        shutil.rmtree(os.path.join(frames_folder_u, i))
                except Exception as e:
                    return jsonify({'error': f'Error clearing uploads folder: {e}'})
                # os.remove(os.path.join(UPLOAD_FOLDER+"/frames", i))
        
        # copy to new folder (from static to upload)
        for idx, i in enumerate(files):
            shutil.copy2(os.path.join(frames_folder, i), frames_folder_u)

        # Redirect to the thumbnails page after extracting frames
        return redirect(url_for('thumbnails'))

    return jsonify({'error': 'Invalid file format'})

@app.route('/thumbnails')
def thumbnails(limit_display = 100):
    frames_folder = os.path.join(STATIC_FOLDER, 'frames')
    
    # for jpgfile in glob.iglob(os.path.join(frames_src_folder, "*.jpg"))[:50]:
    #     shutil.copy(jpgfile, frames_dest_folder)
    
    frame_files = sorted([f for f in os.listdir(frames_folder) if f.endswith('.jpg')])[:limit_display]
    thumbnails = [{'filename': f, 'path': f} for f in natsort.natsorted(frame_files)]

    return render_template('thumbnails.html', thumbnails=thumbnails)

# @app.route('/show_result/<filename>')
# def show_result(filename):
#     # Add your image classification code here
    
#     img_path = f'app/static/{filename}'
#     # file.save(img_path)

#     img_array = prepare_image(img_path)
#     predictions = model.predict(img_array)
#     decoded_predictions = decode_predictions(predictions, top=3)[0]

#     result = [{'label': label, 'probability': float(prob)} for (_, label, prob) in decoded_predictions]
 
#     # For demonstration purposes, we'll just show the filename as the result
#     # result = {'label': 'Demo Label', 'probability': 'Demo Probability'}

#     return render_template('results.html', filename=filename, result=result)

@app.route('/clear_data', methods=['POST'])
def clear_data():
    try:
        # Clear the contents of the 'static' folder
        static_folder = os.path.join(app.root_path, 'static', "frames")
        for filename in os.listdir(static_folder):
            file_path = os.path.join(static_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                return jsonify({'error': f'Error clearing static frames folder: {e}'})

        # Clear the contents of the 'uploads' folder
        uploads_folder = os.path.join(app.root_path, 'uploads')
        for filename in os.listdir(uploads_folder):
            file_path = os.path.join(uploads_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                return jsonify({'error': f'Error clearing uploads folder: {e}'})

        return jsonify({'message': 'Data cleared successfully'})

    except Exception as e:
        return jsonify({'error': f'Error clearing data: {e}'})


@app.route('/classify_button/<filename>')
def classify_button(filename):
    # Redirect to the classification page with the selected filename
    return redirect(url_for('classify_image', filename=filename))

# @app.route('/classify_image/<filename>')
# def classify_image(filename):

#     # Add your image classification code here
#     img_path = f'app/static/{filename}'
#     # file.save(img_path)

#     img_array = prepare_image(img_path)
#     predictions = model.predict(img_array)
#     decoded_predictions = decode_predictions(predictions, top=3)[0]

#     result = [{'label': label, 'probability': float(prob)} for (_, label, prob) in decoded_predictions]
 
#     # For demonstration purposes, we'll just show the filename as the result
#     # result = {'label': 'Demo Label', 'probability': 'Demo Probability'}

#     return render_template('classification_result.html', filename=filename, result=result)

@app.route('/classify_image/<filename>', methods=['GET', 'POST'])
def classify_image(filename):
    if request.method == 'POST':
        # Add your I3D model classification code here
        img_path = os.path.join(STATIC_FOLDER, "frames", filename)
        # file.save(img_path)

        img_array = prepare_image(img_path)
        predictions = model.predict(img_array)
        decoded_predictions = decode_predictions(predictions, top=3)[0]

        results = [{'label': label, 'probability': float(prob)} for (_, label, prob) in decoded_predictions]
        # print(results)

        return render_template('classification_results.html', filename=filename, results=results)

    # If it's a GET request, you can handle it differently if needed
    return render_template('thumbnails.html', thumbnails=thumbnails)


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], host='0.0.0.0', port=80)
