"""
MediSynth AI - Machine Learning Model Training
==============================================
Trains a Random Forest classifier for patient risk prediction.

Usage:
    python scripts/train_model.py

Environment variables:
    MONGO_URI   Optional MongoDB connection string. If omitted, CSV data is used.
"""

from __future__ import annotations

import os
from pathlib import Path

import joblib
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "patients_data.csv"
MODEL_FILE = BASE_DIR / "models" / "triage_model.pkl"

load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "medisynth_db"
COLLECTION_NAME = "patients"


def fetch_data() -> pd.DataFrame:
    """Fetch patient data from MongoDB when configured, otherwise use the CSV dataset."""
    if MONGO_URI:
        print("Connecting to MongoDB...")
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            collection = client[DATABASE_NAME][COLLECTION_NAME]
            data = list(collection.find())
            client.close()

            if data:
                df = pd.DataFrame(data)
                if "_id" in df.columns:
                    df = df.drop(columns=["_id"])
                print(f"✓ Loaded {len(df)} records from MongoDB")
                return df

            print("⚠️ MongoDB collection is empty. Falling back to CSV.")
        except Exception as exc:
            print(f"⚠️ MongoDB unavailable: {exc}")
            print("→ Falling back to CSV dataset")
    else:
        print("ℹ️ MONGO_URI not set. Using local CSV dataset.")

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_FILE}. Run scripts/generate_data.py first."
        )

    df = pd.read_csv(DATA_FILE)
    print(f"✓ Loaded {len(df)} records from CSV")
    return df


def preprocess_data(df: pd.DataFrame):
    """Prepare features and target labels for training."""
    print("\nPreprocessing data...")

    df = df.copy()
    df["risk_level_encoded"] = df["risk_level"].map({"Low": 0, "High": 1})

    feature_columns = ["age", "heart_rate", "systolic_bp"]
    X = df[feature_columns]
    y = df["risk_level_encoded"]

    print(f"Features: {feature_columns}")
    print(f"Low risk samples: {(y == 0).sum()}")
    print(f"High risk samples: {(y == 1).sum()}")
    return X, y


def train_model(X: pd.DataFrame, y: pd.Series):
    """Train the classifier and return the trained model with test data."""
    print("\n" + "=" * 60)
    print("TRAINING RANDOM FOREST CLASSIFIER")
    print("=" * 60)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    print("✓ Training complete")
    print("\nFeature importance:")
    for feature, importance in zip(X.columns, model.feature_importances_):
        print(f"  {feature:15s}: {importance:.4f}")

    return model, X_test, y_test


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> None:
    """Print core evaluation metrics for the trained classifier."""
    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print(f"Accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")
    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["Low Risk", "High Risk"],
            digits=4,
        )
    )

    print("Confusion matrix:")
    print(f"                Predicted Low  Predicted High")
    print(f"Actual Low      {cm[0][0]:13d}  {cm[0][1]:14d}")
    print(f"Actual High     {cm[1][0]:13d}  {cm[1][1]:14d}")


def save_model(model) -> None:
    """Persist the trained model into the models folder."""
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    print(f"\n✓ Model saved to {MODEL_FILE}")


def main() -> None:
    """Run the full training pipeline."""
    print("=" * 60)
    print("MediSynth AI - ML Model Training")
    print("=" * 60)

    df = fetch_data()
    X, y = preprocess_data(df)
    model, X_test, y_test = train_model(X, y)
    evaluate_model(model, X_test, y_test)
    save_model(model)

    print("\n✓ Training pipeline complete")


if __name__ == "__main__":
    main()
