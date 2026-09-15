import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'findit-secret-key-college-lost-found-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///findit.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload

    # Matching Weights (Default 40% Text, 20% Category, 15% Location, 15% Time, 10% Image)
    MATCH_WEIGHT_TEXT = 0.40
    MATCH_WEIGHT_CATEGORY = 0.20
    MATCH_WEIGHT_LOCATION = 0.15
    MATCH_WEIGHT_TIME = 0.15
    MATCH_WEIGHT_IMAGE = 0.10

    # Matching Thresholds (%)
    THRESHOLD_HIGH = 80.0
    THRESHOLD_MEDIUM = 60.0
    THRESHOLD_LOW = 45.0
    # Scores 0 - 44.99 are NOT_SUITABLE

    # Verification Thresholds (%)
    VERIFICATION_STRONG = 75.0
    VERIFICATION_PARTIAL = 50.0

    # Pagination
    MATCHES_PER_PAGE = 10
