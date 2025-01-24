import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///courage_fx.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Upload config
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Email config
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Deriv API config
    DERIV_APP_ID = os.environ.get('DERIV_APP_ID')
    DERIV_API_URL = 'wss://ws.binaryws.com/websockets/v3'
    
    # Bot config
    MAX_BOTS_PER_USER = 5
    DEFAULT_INVESTMENT_LIMIT = 1000
    MIN_STAKE_AMOUNT = 1
    MAX_STAKE_AMOUNT = 10000
    
    # PWA config
    PWA_NAME = 'Courage FX'
    PWA_THEME_COLOR = '#1a237e'
    PWA_BACKGROUND_COLOR = '#ffffff'
    PWA_DISPLAY = 'standalone'
    
    # Security config
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
