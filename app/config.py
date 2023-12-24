# config.py

class Config:
    DEBUG = True  # Set to False in production
    SECRET_KEY = 'your_secret_key'
    UPLOAD_FOLDER = 'app/uploads'
    ALLOWED_EXTENSIONS = {'mp4', 'avi'}
