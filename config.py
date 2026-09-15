import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'findit-college-secure-key-2026-prod-secret'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(BASE_DIR, 'findit.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB Max Upload Size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(Config.BASE_DIR, 'test_findit.db')}"
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = os.path.join(Config.BASE_DIR, 'tests', 'test_uploads')
