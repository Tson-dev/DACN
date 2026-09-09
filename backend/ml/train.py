import pickle
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.neighbors import NearestNeighbors
from lightgbm import LGBMRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from backend.config import settings

logger = logging.getLogger(__name__)


def train():
    df = pd.read_csv(settings.DATASET_PATH)
    logger.info(f"Loaded dataset: {len(df)} records, columns: {list(df.columns)}")

    feature_cols = ["Age", "Attendance_Pct", "Study_Hours_Per_Day",
                    "Sleep_Hours", "Social_Hours_Week", "Previous_CGPA"]

    le_gender = LabelEncoder()
    df["Gender_enc"] = le_gender.fit_transform(df["Gender"])

    ohe_major = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    major_encoded = ohe_major.fit_transform(df[["Major"]])
    major_names = [f"Major_{c}" for c in ohe_major.get_feature_names_out(["Major"])]

    X_numeric = df[feature_cols].values
    X_gender = df[["Gender_enc"]].values
    X = np.hstack([X_numeric, X_gender, major_encoded])
    y = df["Final_CGPA"].values

    feature_names = feature_cols + ["Gender"] + major_names

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LGBMRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=6,
        num_leaves=31,
        min_child_samples=20,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        device="cpu",
        verbose=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    logger.info(f"Model performance - MAE: {mae:.4f}, RMSE: {rmse:.4f}, R²: {r2:.4f}")

    knn_scaler = StandardScaler()
    X_scaled = knn_scaler.fit_transform(X)

    knn_model = NearestNeighbors(n_neighbors=settings.KNN_K, metric="euclidean")
    knn_model.fit(X_scaled)

    artifacts = {
        "model": model,
        "label_encoder_gender": le_gender,
        "onehot_encoder_major": ohe_major,
        "knn_features_scaler": knn_scaler,
        "knn_model": knn_model,
        "historical_features": X,
        "historical_final_gpas": y,
        "feature_columns": feature_names,
        "feature_cols_numeric": feature_cols,
    }

    settings.MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(settings.MODEL_PATH, "wb") as f:
        pickle.dump(artifacts, f)
    logger.info(f"Model artifacts saved to {settings.MODEL_PATH}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train()
