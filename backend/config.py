import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory: backend root
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Load .env file from project root if it exists
load_dotenv(PROJECT_ROOT / ".env")

class Config:
    """Base configuration settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_applypilot_ai_2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_jwt_secret_applypilot_ai_2026")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # Storage settings
    STORAGE_DIR = PROJECT_ROOT / "storage"
    RESUME_STORAGE_DIR = STORAGE_DIR / "resumes"
    LOGS_STORAGE_DIR = STORAGE_DIR / "logs"
    
    # Database
    DEFAULT_DB_PATH = (STORAGE_DIR / "applypilot.db").as_posix()
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Automation settings
    AUTOMATION_HEADLESS = os.getenv("AUTOMATION_HEADLESS", "false").lower() == "true"
    DEFAULT_APPLICATION_DELAY_SECONDS = int(os.getenv("DEFAULT_APPLICATION_DELAY_SECONDS", "5"))

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_EXPIRATION_HOURS = 1

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
