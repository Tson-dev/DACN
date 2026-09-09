import os
from pathlib import Path


class Settings:
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASE_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
    DATABASE_PATH = DATABASE_DIR / "app.db"
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

    MODEL_PATH = DATABASE_DIR / "model_artifacts.pkl"
    DATASET_PATH = Path(os.getenv("DATASET_PATH", BASE_DIR / "TrainingData" / "Student_data.csv"))

    SESSION_EXPIRY_HOURS = 24
    COOKIE_NAME = "session_id"
    COOKIE_MAX_AGE = SESSION_EXPIRY_HOURS * 3600

    PASSWORD_MIN_LENGTH = 6

    TARGET_GPA_MIN = 0.01
    TARGET_GPA_MAX = 4.0
    KNN_K = 50

    TIMEZONE = "Asia/Ho_Chi_Minh"

    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "admin123"


settings = Settings()
