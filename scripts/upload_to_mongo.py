"""
MediSynth AI - MongoDB Upload Script
====================================
Uploads the synthetic patient dataset to MongoDB Atlas.

Usage:
    python scripts/upload_to_mongo.py

Environment variables:
    MONGO_URI   MongoDB connection string
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "patients_data.csv"

load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "medisynth_db"
COLLECTION_NAME = "patients"


def load_patient_data() -> pd.DataFrame:
    """Load the generated patient CSV from the project data folder."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Patient dataset not found at {DATA_FILE}. Run scripts/generate_data.py first."
        )

    print(f"⏳ Loading patient records from {DATA_FILE}...")
    df = pd.read_csv(DATA_FILE)
    print(f"✅ Loaded {len(df)} patient records.")
    return df


def get_collection():
    """Connect to MongoDB and return the client and collection."""
    if not MONGO_URI:
        raise EnvironmentError(
            "Missing MONGO_URI. Add it to a local .env file or export it in your shell."
        )

    print("⏳ Connecting to MongoDB Atlas...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    return client, collection


def upload_data() -> None:
    """Replace the collection contents with the latest CSV dataset."""
    df = load_patient_data()
    records = df.to_dict(orient="records")
    client = None

    try:
        client, collection = get_collection()

        print("⏳ Clearing existing patient records...")
        collection.delete_many({})

        print("⏳ Uploading fresh dataset...")
        collection.insert_many(records)

        print("🎉 Upload complete.")
        print(f"Database: {DATABASE_NAME} | Collection: {COLLECTION_NAME}")
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    upload_data()
