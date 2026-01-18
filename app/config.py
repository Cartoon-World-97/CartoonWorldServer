import os
from datetime import timedelta
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

class Config:
    """Base configuration (used by default)"""
    SECRET_KEY = os.getenv("SECRET_KEY", "SERVER_VIDEO")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "wh&*sg ujs3a sa3as1")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)      
    
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{os.getenv('DB_USER', 'root')}:" 
        f"{os.getenv('DB_PASSWORD', '')}@"
        f"{os.getenv('DB_HOST', 'localhost')}/"
        f"{os.getenv('DB_NAME', 'cartoonworld')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ["true", "1", "t"]
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # PayPal Credentials
    PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
    PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
    PAYPAL_ENV = os.getenv("PAYPAL_ENV", "sandbox")  # sandbox / live

    # PayPal Base URL
    PAYPAL_API = (
        "https://api-m.paypal.com"
        if PAYPAL_ENV == "live"
        else "https://api-m.sandbox.paypal.com"
    )

    # Webhook URL
    PAYPAL_WEBHOOK_URL = os.getenv("PAYPAL_WEBHOOK_URL")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
