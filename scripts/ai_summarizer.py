"""
MediSynth AI - Medical Notes Summarizer
=======================================
Creates lightweight AI-style summaries for patient notes in demo mode.

Usage:
    python scripts/ai_summarizer.py

Environment variables:
    MONGO_URI        Optional MongoDB connection string
    OPENAI_API_KEY   Reserved for future real LLM integration
"""

from __future__ import annotations

import os
import random
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "patients_data.csv"

load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_NAME = "medisynth_db"
COLLECTION_NAME = "patients"
DEMO_LIMIT = 5


def initialize_ai_engine() -> None:
    """Initialize demo-mode summarization."""
    print("Initializing AI summarizer...")
    if OPENAI_API_KEY:
        print("ℹ️ OPENAI_API_KEY detected, but this portfolio version runs in demo mode.")
    print("✓ Demo summarization engine ready")
    return None


def fetch_patients(limit: int | None = None) -> pd.DataFrame:
    """Fetch patient records from MongoDB when available, otherwise use CSV."""
    if MONGO_URI:
        print("\nConnecting to MongoDB...")
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            collection = client[DATABASE_NAME][COLLECTION_NAME]
            data = list(collection.find().limit(limit)) if limit else list(collection.find())
            client.close()

            if data:
                df = pd.DataFrame(data)
                if "_id" in df.columns:
                    df = df.drop(columns=["_id"])
                print(f"✓ Loaded {len(df)} patients from MongoDB")
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
    if limit:
        df = df.head(limit)
    print(f"✓ Loaded {len(df)} patients from CSV")
    return df


def summarize_medical_notes(medical_notes: str) -> dict[str, str]:
    """Generate a deterministic demo summary from the original notes."""
    notes_lower = medical_notes.lower()

    conditions = []
    if "chest pain" in notes_lower:
        conditions.append("chest pain")
    if "hypertension" in notes_lower or "blood pressure" in notes_lower:
        conditions.append("hypertension")
    if "diabetes" in notes_lower:
        conditions.append("diabetes mellitus")
    if "respiratory" in notes_lower or "shortness of breath" in notes_lower:
        conditions.append("respiratory distress")
    if "headache" in notes_lower or "dizziness" in notes_lower:
        conditions.append("headaches and dizziness")
    if "abdominal pain" in notes_lower or "nausea" in notes_lower:
        conditions.append("abdominal discomfort")
    if "back pain" in notes_lower:
        conditions.append("lower back pain")
    if "kidney" in notes_lower:
        conditions.append("chronic kidney disease")
    if "fever" in notes_lower or "fatigue" in notes_lower:
        conditions.append("fever and fatigue")
    if "asthma" in notes_lower:
        conditions.append("asthma")

    status = "stable condition"
    if "distress" in notes_lower:
        status = "moderate distress"
    elif "alert and oriented" in notes_lower:
        status = "alert and oriented"

    next_steps = []
    if "follow-up" in notes_lower:
        next_steps.append("follow-up recommended")
    if "monitoring" in notes_lower or "monitor" in notes_lower:
        next_steps.append("requires monitoring")
    if "lab work" in notes_lower:
        next_steps.append("lab work ordered")
    if "referral" in notes_lower:
        next_steps.append("specialist referral needed")
    if "medication" in notes_lower or "prescribed" in notes_lower:
        next_steps.append("medication prescribed")

    condition_text = (
        f"Patient presents with {' and '.join(conditions[:2])}"
        if conditions
        else "Patient presents for routine evaluation"
    )
    action_text = ", ".join(next_steps[:2]) if next_steps else "continued observation advised"
    summary = f"{condition_text}. Patient shows {status}, {action_text}."

    medication_lookup = {
        "hypertension": ["Lisinopril", "Amlodipine", "Losartan"],
        "chest pain": ["Aspirin", "Nitroglycerin"],
        "diabetes mellitus": ["Metformin", "Insulin"],
        "respiratory distress": ["Albuterol", "Prednisone"],
        "lower back pain": ["Ibuprofen", "Acetaminophen"],
        "chronic kidney disease": ["Furosemide"],
        "fever and fatigue": ["Acetaminophen"],
    }

    medications = []
    for condition in conditions:
        if condition in medication_lookup:
            medications.extend(random.sample(medication_lookup[condition], 1))

    medications_text = ", ".join(sorted(set(medications))[:3]) if medications else "None mentioned in notes"
    return {"summary": summary, "medications": medications_text}


def process_patients(df: pd.DataFrame) -> pd.DataFrame:
    """Apply demo summaries to each patient record."""
    print("\n" + "=" * 60)
    print("PROCESSING PATIENTS WITH AI")
    print("=" * 60)

    summaries = []
    medications_list = []

    for index, row in df.iterrows():
        print(f"[{index + 1}/{len(df)}] Processing {row['name']} ({row['patient_id']})...")
        result = summarize_medical_notes(row["medical_notes"])
        summaries.append(result["summary"])
        medications_list.append(result["medications"])

    processed_df = df.copy()
    processed_df["ai_summary"] = summaries
    processed_df["medications"] = medications_list
    return processed_df


def display_results(df: pd.DataFrame) -> None:
    """Print readable sample results to the console."""
    print("\n" + "=" * 60)
    print("AI SUMMARIZATION RESULTS")
    print("=" * 60)

    for index, row in df.iterrows():
        print(f"\nPatient #{index + 1}: {row['name']} ({row['patient_id']})")
        print(f"Risk Level: {row['risk_level']}")
        print(f"Original Notes: {row['medical_notes']}")
        print(f"AI Summary: {row['ai_summary']}")
        print(f"Medications: {row['medications']}")


def save_results(df: pd.DataFrame) -> None:
    """Persist AI summaries back to MongoDB when configured."""
    if not MONGO_URI:
        print("\nℹ️ MONGO_URI not set. Skipping MongoDB update.")
        return

    print("\nSaving AI summaries to MongoDB...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    collection = client[DATABASE_NAME][COLLECTION_NAME]

    updated_count = 0
    for _, row in df.iterrows():
        result = collection.update_one(
            {"patient_id": row["patient_id"]},
            {
                "$set": {
                    "ai_summary": row["ai_summary"],
                    "medications": row["medications"],
                }
            },
        )
        if result.matched_count > 0:
            updated_count += 1

    client.close()
    print(f"✓ Updated {updated_count} records in MongoDB")


def main() -> None:
    """Run the summarization pipeline."""
    print("=" * 60)
    print("MediSynth AI - Medical Summarizer")
    print("=" * 60)

    initialize_ai_engine()
    df = fetch_patients(limit=DEMO_LIMIT)
    processed_df = process_patients(df)
    display_results(processed_df)
    save_results(processed_df)

    print("\n✓ Summarization pipeline complete")


if __name__ == "__main__":
    main()
