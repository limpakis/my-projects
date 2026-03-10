"""
MediSynth AI - Synthetic Patient Data Generator
================================================
Healthcare Triage System Training Data

Installation Requirements:
---------------------------
pip install faker pandas numpy

Usage:
------
python generate_data.py
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from pathlib import Path

# Initialize Faker
fake = Faker()

# Set random seed for reproducibility
np.random.seed(42)
Faker.seed(42)

# Number of patient records to generate
NUM_PATIENTS = 200
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / 'data'

def generate_medical_notes():
    """
    Generate realistic medical notes by combining random medical phrases.
    Returns a paragraph with 3-5 sentences.
    """
    complaints = [
        "Patient complains of chest pain radiating to left arm.",
        "Patient reports persistent headaches and dizziness.",
        "Patient presents with shortness of breath on exertion.",
        "Patient experiencing abdominal pain and nausea.",
        "Patient reports fever and fatigue lasting 3 days.",
        "Patient complains of lower back pain.",
        "Patient presents with acute respiratory distress.",
        "Patient reports chronic joint pain and stiffness."
    ]
    
    history = [
        "History of hypertension managed with medication.",
        "No known allergies reported.",
        "Past medical history includes diabetes mellitus type 2.",
        "Family history of cardiovascular disease.",
        "Previous hospitalizations for asthma exacerbation.",
        "History of smoking, quit 5 years ago.",
        "Known history of chronic kidney disease stage 3.",
        "Past surgical history includes appendectomy."
    ]
    
    assessment = [
        "Vital signs stable at time of assessment.",
        "Patient appears alert and oriented to time, place, and person.",
        "Physical examination reveals no acute abnormalities.",
        "Patient shows signs of moderate distress.",
        "Cardiovascular examination unremarkable.",
        "Respiratory sounds clear bilaterally.",
        "Patient requires further monitoring.",
        "Condition appears stable with current treatment."
    ]
    
    plan = [
        "Recommend follow-up in 2 weeks.",
        "Prescribed medication for symptom management.",
        "Lab work ordered to rule out underlying conditions.",
        "Patient advised to monitor symptoms and return if worsening.",
        "Referral to specialist recommended.",
        "Continue current medication regimen.",
        "Patient education provided regarding condition management."
    ]
    
    # Randomly select 3-5 sentences from different categories
    num_sentences = random.randint(3, 5)
    notes = []
    
    # Always include a complaint
    notes.append(random.choice(complaints))
    
    # Add history if we need more sentences
    if num_sentences > 1:
        notes.append(random.choice(history))
    
    # Add assessment if we need more sentences
    if num_sentences > 2:
        notes.append(random.choice(assessment))
    
    # Add plan if we need more sentences
    if num_sentences > 3:
        notes.append(random.choice(plan))
    
    # If we still need more, add another random one
    if num_sentences > 4:
        notes.append(random.choice(assessment + plan))
    
    return " ".join(notes)

def calculate_risk_level(heart_rate, systolic_bp):
    """
    Determine risk level based on vital signs.
    
    Logic:
    - High: heart_rate > 110 OR systolic_bp > 150
    - Low: otherwise
    """
    if heart_rate > 110 or systolic_bp > 150:
        return "High"
    else:
        return "Low"

def generate_patient_data(num_patients=NUM_PATIENTS):
    """
    Generate synthetic patient data for testing.
    
    Returns:
        pandas.DataFrame: DataFrame containing patient records
    """
    print(f"Generating {num_patients} patient records...")
    
    patients = []
    
    for i in range(1, num_patients + 1):
        # Generate patient data
        patient_id = f"PAT{i:05d}"  # Format: PAT00001, PAT00002, etc.
        name = fake.name()
        age = random.randint(18, 90)
        heart_rate = random.randint(60, 140)
        systolic_bp = random.randint(90, 180)
        diastolic_bp = random.randint(60, 120)
        medical_notes = generate_medical_notes()
        risk_level = calculate_risk_level(heart_rate, systolic_bp)
        
        # Additional details
        room_number = f"{random.randint(1, 5)}{random.randint(0, 9):02d}"  # Format: 101-599
        admission_date = fake.date_between(start_date='-30d', end_date='today').strftime('%Y-%m-%d')
        blood_type = random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
        temperature = round(random.uniform(97.0, 102.0), 1)  # Fahrenheit
        oxygen_saturation = random.randint(88, 100)  # SpO2 %
        
        # Create patient record
        patient = {
            'patient_id': patient_id,
            'name': name,
            'age': age,
            'heart_rate': heart_rate,
            'systolic_bp': systolic_bp,
            'diastolic_bp': diastolic_bp,
            'medical_notes': medical_notes,
            'risk_level': risk_level,
            'room_number': room_number,
            'admission_date': admission_date,
            'blood_type': blood_type,
            'temperature': temperature,
            'oxygen_saturation': oxygen_saturation
        }
        
        patients.append(patient)
    
    # Convert to DataFrame
    df = pd.DataFrame(patients)
    
    return df

def display_summary(df):
    """Display summary statistics"""
    print("\n" + "="*60)
    print("Data Generation Complete!")
    print("="*60)
    print(f"\nTotal Patients Generated: {len(df)}")
    print(f"\nRisk Level Distribution:")
    print(df['risk_level'].value_counts())
    print(f"\nAge Statistics:")
    print(f"  Mean: {df['age'].mean():.1f}")
    print(f"  Range: {df['age'].min()} - {df['age'].max()}")
    print(f"\nHeart Rate Statistics:")
    print(f"  Mean: {df['heart_rate'].mean():.1f}")
    print(f"  Range: {df['heart_rate'].min()} - {df['heart_rate'].max()}")
    print(f"\nBlood Pressure (Systolic) Statistics:")
    print(f"  Mean: {df['systolic_bp'].mean():.1f}")
    print(f"  Range: {df['systolic_bp'].min()} - {df['systolic_bp'].max()}")

def save_to_csv(df):
    """Save DataFrame to CSV file"""
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    output_file = DATA_DIR / 'patients_data.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Data saved to: {output_file}")
    
    return str(output_file)

def display_sample(df):
    """Display sample records"""
    print("\n" + "="*60)
    print("Sample Records (First 3):")
    print("="*60)
    print(df.head(3).to_string())

def main():
    """Main execution function"""
    
    print("="*60)
    print("MediSynth AI - Synthetic Patient Data Generator")
    print("="*60)
    print()
    
    try:
        # Step 1: Generate patient data
        df = generate_patient_data()
        
        # Step 2: Display summary
        display_summary(df)
        
        # Step 3: Save to CSV
        save_to_csv(df)
        
        # Step 4: Display sample records
        display_sample(df)
        
        print("\n" + "="*60)
        print("✓ DATA GENERATION COMPLETE!")
        print("="*60)
        print("\nNext Steps:")
        print("  1. Run: python upload_to_mongo.py")
        print("  2. Upload data to MongoDB Atlas")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error during data generation: {e}")
        raise

if __name__ == "__main__":
    main()
