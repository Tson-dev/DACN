import pickle
import logging
from pathlib import Path

import numpy as np

from backend.config import settings

logger = logging.getLogger(__name__)


class MLService:
    def __init__(self):
        self.model = None
        self.label_encoder_gender = None
        self.onehot_encoder_major = None
        self.knn_features_scaler = None
        self.knn_model = None
        self.historical_features = None
        self.historical_final_gpas = None
        self.feature_columns = None
        self.feature_cols_numeric = None
        self.loaded = False

    def load(self):
        if not settings.MODEL_PATH.exists():
            raise FileNotFoundError(f"Model artifacts not found at {settings.MODEL_PATH}. Run training first.")

        with open(settings.MODEL_PATH, "rb") as f:
            artifacts = pickle.load(f)

        self.model = artifacts["model"]
        self.label_encoder_gender = artifacts["label_encoder_gender"]
        self.onehot_encoder_major = artifacts["onehot_encoder_major"]
        self.knn_features_scaler = artifacts["knn_features_scaler"]
        self.knn_model = artifacts["knn_model"]
        self.historical_features = artifacts["historical_features"]
        self.historical_final_gpas = artifacts["historical_final_gpas"]
        self.feature_columns = artifacts["feature_columns"]
        self.feature_cols_numeric = artifacts["feature_cols_numeric"]
        self.loaded = True
        logger.info("ML model loaded successfully")

    def _encode_features(self, profile) -> np.ndarray:
        import pandas as pd
        gender_enc = self.label_encoder_gender.transform([profile.gender])[0] if profile.gender else 0

        major_df = pd.DataFrame({"Major": [profile.major or "Unknown"]})
        major_arr = self.onehot_encoder_major.transform(major_df)[0]

        numeric = np.array([
            profile.age or 0,
            profile.attendance_percentage or 0,
            profile.study_hours_per_day or 0,
            profile.sleep_hours_per_day or 0,
            profile.social_hours_per_week or 0,
            profile.previous_cgpa or 0,
        ])

        return np.hstack([numeric, [gender_enc], major_arr])

    def predict(self, profile, target_gpa: float) -> tuple[float, float, int]:
        if not self.loaded:
            raise RuntimeError("ML model not loaded")

        features = self._encode_features(profile)
        predicted_gpa = float(self.model.predict([features])[0])

        scaled = self.knn_features_scaler.transform([features])
        distances, indices = self.knn_model.kneighbors(scaled)

        similar_gpas = self.historical_final_gpas[indices[0]]
        meeting_target = int(np.sum(similar_gpas >= target_gpa))
        total = len(similar_gpas)

        probability = (meeting_target / total * 100) if total > 0 else 50.0

        return predicted_gpa, probability, total


ml_service = MLService()
