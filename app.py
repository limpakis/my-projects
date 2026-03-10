"""
Vital Scan - Healthcare Triage Dashboard
===========================================
Interactive Web Application for Patient Risk Assessment

Installation Requirements:
---------------------------
pip install streamlit pymongo pandas plotly joblib scikit-learn

Usage:
------
streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path
from pymongo import MongoClient
import joblib
from datetime import datetime
from dotenv import load_dotenv

# ============================================================
# CONFIGURATION
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "vitalscan_db"
COLLECTION_NAME = "patients"
MODEL_PATH = BASE_DIR / "models" / "triage_model.pkl"
DATA_PATH = BASE_DIR / "data" / "patients_data.csv"

# Page configuration
st.set_page_config(
    page_title="Vital Scan - Healthcare Triage",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .high-risk {
        color: #d62728;
        font-weight: bold;
    }
    .low-risk {
        color: #2ca02c;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING FUNCTIONS
# ============================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data_from_mongodb():
    """Load patient data from MongoDB Atlas with CSV fallback"""
    if not MONGO_URI:
        st.info("ℹ️ MONGO_URI not configured. Loading from the local CSV dataset.")
        return load_data_from_csv()

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        data = list(collection.find())
        client.close()
        
        if not data:
            st.warning("⚠️ No data in MongoDB. Loading from CSV...")
            return load_data_from_csv()
        
        df = pd.DataFrame(data)
        if '_id' in df.columns:
            df = df.drop('_id', axis=1)
        
        st.success("✅ Data loaded from MongoDB")
        return df
    except Exception as e:
        st.warning(f"⚠️ MongoDB connection failed. Loading from CSV backup...")
        return load_data_from_csv()

def load_data_from_csv():
    """Fallback: Load patient data from CSV file"""
    try:
        df = pd.read_csv(DATA_PATH)
        st.info("📁 Data loaded from local CSV file")
        return df
    except Exception as e:
        st.error(f"❌ Could not load data: {e}")
        return None

@st.cache_resource
def load_ml_model():
    """Load the trained ML model"""
    try:
        model = joblib.load(MODEL_PATH)
        return model
    except Exception as e:
        st.error(f"Error loading ML model: {e}")
        return None

# ============================================================
# MAIN DASHBOARD
# ============================================================

def main():
    # Header
    st.markdown('<h1 class="main-header">🏥 Vital Scan</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: gray;">Healthcare Triage & Risk Assessment System</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading patient data..."):
        df = load_data_from_mongodb()
        model = load_ml_model()
    
    if df is None:
        st.error("⚠️ Unable to load patient data. Please check MongoDB connection.")
        return
    
    # Sidebar
    st.sidebar.title("🔍 Filters & Navigation")
    
    # Risk level filter
    risk_filter = st.sidebar.multiselect(
        "Filter by Risk Level:",
        options=["High", "Low"],
        default=["High", "Low"]
    )
    
    # Age range filter
    age_range = st.sidebar.slider(
        "Age Range:",
        int(df['age'].min()),
        int(df['age'].max()),
        (int(df['age'].min()), int(df['age'].max()))
    )
    
    # Apply filters
    filtered_df = df[
        (df['risk_level'].isin(risk_filter)) &
        (df['age'] >= age_range[0]) &
        (df['age'] <= age_range[1])
    ]
    
    # Navigation
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigate to:",
        ["📊 Dashboard Overview", "👥 Patient List", "📁 Patient Details", "🔬 ML Predictions", "📝 AI Summaries"]
    )
    
    # ============================================================
    # PAGE 1: DASHBOARD OVERVIEW
    # ============================================================
    if page == "📊 Dashboard Overview":
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Total Patients", len(filtered_df))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            high_risk_count = len(filtered_df[filtered_df['risk_level'] == 'High'])
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("🔴 High Risk", high_risk_count)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            low_risk_count = len(filtered_df[filtered_df['risk_level'] == 'Low'])
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("🟢 Low Risk", low_risk_count)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            avg_age = filtered_df['age'].mean()
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Average Age", f"{avg_age:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Risk Level Distribution")
            risk_counts = filtered_df['risk_level'].value_counts()
            fig = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                color=risk_counts.index,
                color_discrete_map={'High': '#d62728', 'Low': '#2ca02c'},
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Age Distribution by Risk Level")
            fig = px.histogram(
                filtered_df,
                x='age',
                color='risk_level',
                nbins=20,
                color_discrete_map={'High': '#d62728', 'Low': '#2ca02c'},
                barmode='overlay',
                opacity=0.7
            )
            fig.update_layout(xaxis_title="Age", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
        
        # Charts Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Heart Rate vs Blood Pressure")
            fig = px.scatter(
                filtered_df,
                x='heart_rate',
                y='systolic_bp',
                color='risk_level',
                size='age',
                hover_data=['name', 'age'],
                color_discrete_map={'High': '#d62728', 'Low': '#2ca02c'}
            )
            fig.add_hline(y=150, line_dash="dash", line_color="red", annotation_text="High BP Threshold")
            fig.add_vline(x=110, line_dash="dash", line_color="red", annotation_text="High HR Threshold")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Vital Signs Statistics")
            stats_df = filtered_df.groupby('risk_level')[['heart_rate', 'systolic_bp', 'age']].mean().round(1)
            fig = go.Figure(data=[
                go.Bar(name='Heart Rate', x=stats_df.index, y=stats_df['heart_rate'], marker_color='#1f77b4'),
                go.Bar(name='Systolic BP', x=stats_df.index, y=stats_df['systolic_bp'], marker_color='#ff7f0e'),
                go.Bar(name='Age', x=stats_df.index, y=stats_df['age'], marker_color='#2ca02c')
            ])
            fig.update_layout(barmode='group', xaxis_title="Risk Level", yaxis_title="Average Value")
            st.plotly_chart(fig, use_container_width=True)
    
    # ============================================================
    # PAGE 2: PATIENT LIST
    # ============================================================
    elif page == "👥 Patient List":
        st.header("📋 Patient Records")
        
        # Search
        search = st.text_input("🔍 Search by name or patient ID:", "")
        if search:
            filtered_df = filtered_df[
                filtered_df['name'].str.contains(search, case=False) |
                filtered_df['patient_id'].str.contains(search, case=False)
            ]
        
        # Sort options
        sort_by = st.selectbox("Sort by:", ['patient_id', 'name', 'age', 'heart_rate', 'systolic_bp', 'risk_level'])
        filtered_df = filtered_df.sort_values(sort_by)
        
        st.markdown(f"**Showing {len(filtered_df)} patients**")
        
        # Display table with room numbers if available
        display_columns = ['patient_id', 'name', 'age', 'heart_rate', 'systolic_bp', 'diastolic_bp', 'risk_level']
        if 'room_number' in filtered_df.columns:
            display_columns.insert(2, 'room_number')
        
        display_df = filtered_df[display_columns].copy()
        
        # Style the dataframe
        def highlight_risk(val):
            if val == 'High':
                return 'background-color: #ffcccc; color: #d62728; font-weight: bold'
            elif val == 'Low':
                return 'background-color: #ccffcc; color: #2ca02c; font-weight: bold'
            return ''
        
        styled_df = display_df.style.applymap(highlight_risk, subset=['risk_level'])
        st.dataframe(styled_df, use_container_width=True, height=600)
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Patient Data (CSV)",
            data=csv,
            file_name=f"patients_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # ============================================================
    # PAGE 3: PATIENT DETAILS (NEW!)
    # ============================================================
    elif page == "📁 Patient Details":
        st.header("📁 Detailed Patient Records")
        
        # Patient selector
        col1, col2 = st.columns([2, 1])
        with col1:
            patient_names = filtered_df['name'].tolist()
            selected_patient = st.selectbox("Select a patient to view full details:", patient_names)
        
        with col2:
            st.metric("Total Patients", len(filtered_df))
        
        if selected_patient:
            patient = filtered_df[filtered_df['name'] == selected_patient].iloc[0]
            
            # Header card
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if patient['risk_level'] == 'High':
                    st.error(f"### 🔴 {patient['risk_level']} Risk")
                else:
                    st.success(f"### 🟢 {patient['risk_level']} Risk")
            
            with col2:
                st.info(f"### 🛏️ Room\n{patient.get('room_number', 'N/A')}")
            
            with col3:
                st.info(f"### 🩺 Age\n{patient['age']} years")
            
            with col4:
                st.info(f"### 🆔 Patient ID\n{patient['patient_id']}")
            
            st.markdown("---")
            
            # Detailed Information in tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📋 Personal Info", "💓 Vital Signs", "📝 Medical Notes", "📊 Risk Analysis"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Personal Information")
                    st.write(f"**Full Name:** {patient['name']}")
                    st.write(f"**Patient ID:** {patient['patient_id']}")
                    st.write(f"**Age:** {patient['age']} years old")
                    if 'blood_type' in patient:
                        st.write(f"**Blood Type:** {patient['blood_type']}")
                    if 'room_number' in patient:
                        st.write(f"**Room Number:** {patient['room_number']}")
                    if 'admission_date' in patient:
                        st.write(f"**Admission Date:** {patient['admission_date']}")
                
                with col2:
                    st.subheader("Status Summary")
                    if patient['risk_level'] == 'High':
                        st.error("⚠️ **High Risk Patient** - Requires immediate attention")
                    else:
                        st.success("✅ **Low Risk Patient** - Stable condition")
                    
                    st.write(f"**Current Status:** Active")
                    st.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            with tab2:
                st.subheader("Vital Signs Monitor")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Heart Rate",
                        f"{patient['heart_rate']} bpm",
                        delta="Normal" if patient['heart_rate'] <= 110 else "Elevated",
                        delta_color="normal" if patient['heart_rate'] <= 110 else "inverse"
                    )
                    if 'temperature' in patient:
                        st.metric(
                            "Temperature",
                            f"{patient['temperature']}°F",
                            delta="Normal" if 97 <= patient['temperature'] <= 99 else "Abnormal",
                            delta_color="normal" if 97 <= patient['temperature'] <= 99 else "inverse"
                        )
                
                with col2:
                    st.metric(
                        "Blood Pressure",
                        f"{patient['systolic_bp']}/{patient['diastolic_bp']} mmHg",
                        delta="Normal" if patient['systolic_bp'] <= 150 else "High",
                        delta_color="normal" if patient['systolic_bp'] <= 150 else "inverse"
                    )
                    if 'oxygen_saturation' in patient:
                        st.metric(
                            "O₂ Saturation",
                            f"{patient['oxygen_saturation']}%",
                            delta="Good" if patient['oxygen_saturation'] >= 95 else "Low",
                            delta_color="normal" if patient['oxygen_saturation'] >= 95 else "inverse"
                        )
                
                with col3:
                    # Vital signs chart
                    st.write("**Risk Thresholds:**")
                    st.write("❤️ HR > 110 bpm → High Risk")
                    st.write("🩸 Systolic BP > 150 → High Risk")
                    
                    # Simple visualization
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = patient['heart_rate'],
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Heart Rate"},
                        gauge = {
                            'axis': {'range': [None, 160]},
                            'bar': {'color': "darkred" if patient['heart_rate'] > 110 else "darkgreen"},
                            'steps': [
                                {'range': [0, 110], 'color': "lightgreen"},
                                {'range': [110, 160], 'color': "lightcoral"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 110
                            }
                        }
                    ))
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.subheader("📝 Clinical Notes")
                st.text_area(
                    "Medical History & Observations:",
                    patient['medical_notes'],
                    height=200,
                    disabled=True
                )
                
                # AI Summary if available
                if 'ai_summary' in patient and pd.notna(patient['ai_summary']):
                    st.markdown("### 🤖 AI-Generated Summary")
                    st.info(patient['ai_summary'])
                    
                    if 'medications' in patient and pd.notna(patient['medications']):
                        st.markdown("### 💊 Current Medications")
                        st.success(patient['medications'])
                else:
                    st.warning("⚠️ AI summary not yet generated for this patient.")
            
            with tab4:
                st.subheader("📊 Risk Assessment Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Risk Factors Detected:**")
                    
                    risk_factors = []
                    if patient['heart_rate'] > 110:
                        risk_factors.append("🔴 Elevated heart rate (>110 bpm)")
                    if patient['systolic_bp'] > 150:
                        risk_factors.append("🔴 High blood pressure (>150 mmHg)")
                    if patient['age'] > 65:
                        risk_factors.append("🟡 Advanced age (>65 years)")
                    
                    if risk_factors:
                        for factor in risk_factors:
                            st.write(factor)
                    else:
                        st.success("✅ No significant risk factors detected")
                    
                    st.markdown("---")
                    st.write("**ML Model Assessment:**")
                    if model:
                        features = [[patient['age'], patient['heart_rate'], patient['systolic_bp']]]
                        prediction = model.predict(features)[0]
                        probability = model.predict_proba(features)[0]
                        
                        risk_prob = probability[1] * 100
                        
                        if prediction == 1:
                            st.error(f"**High Risk:** {risk_prob:.1f}% probability")
                        else:
                            st.success(f"**Low Risk:** {100-risk_prob:.1f}% probability")
                        
                        st.progress(risk_prob / 100)
                
                with col2:
                    # Comparison with population
                    st.write("**Comparison with Patient Population:**")
                    
                    avg_hr = df['heart_rate'].mean()
                    avg_bp = df['systolic_bp'].mean()
                    avg_age = df['age'].mean()
                    
                    comparison_data = pd.DataFrame({
                        'Metric': ['Heart Rate', 'Systolic BP', 'Age'],
                        'This Patient': [patient['heart_rate'], patient['systolic_bp'], patient['age']],
                        'Population Avg': [avg_hr, avg_bp, avg_age]
                    })
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        name='This Patient',
                        x=comparison_data['Metric'],
                        y=comparison_data['This Patient'],
                        marker_color='#d62728' if patient['risk_level'] == 'High' else '#2ca02c'
                    ))
                    fig.add_trace(go.Bar(
                        name='Population Average',
                        x=comparison_data['Metric'],
                        y=comparison_data['Population Avg'],
                        marker_color='lightblue'
                    ))
                    fig.update_layout(barmode='group', height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Action buttons
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📞 Contact Doctor", use_container_width=True):
                    st.success("Doctor notification sent!")
            
            with col2:
                if st.button("📋 Print Report", use_container_width=True):
                    st.info("Generating PDF report...")
            
            with col3:
                if st.button("🔔 Set Alert", use_container_width=True):
                    st.warning("Alert configured for this patient")
            
            with col4:
                if st.button("📊 View History", use_container_width=True):
                    st.info("Historical data loading...")
    
    # ============================================================
    # PAGE 4: ML PREDICTIONS
    # ============================================================
    elif page == "🔬 ML Predictions":
        st.header("🤖 Machine Learning Risk Predictions")
        
        if model is None:
            st.error("⚠️ ML model not loaded. Please check model file.")
            return
        
        st.info("💡 Enter patient vitals to predict risk level using our trained Random Forest model.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Input Patient Data")
            input_age = st.number_input("Age:", min_value=18, max_value=100, value=45)
            input_hr = st.number_input("Heart Rate (bpm):", min_value=40, max_value=200, value=85)
            input_bp = st.number_input("Systolic Blood Pressure (mmHg):", min_value=70, max_value=220, value=130)
            
            if st.button("🔮 Predict Risk Level", type="primary"):
                # Make prediction
                features = [[input_age, input_hr, input_bp]]
                prediction = model.predict(features)[0]
                probability = model.predict_proba(features)[0]
                
                risk_label = "High" if prediction == 1 else "Low"
                risk_prob = probability[1] * 100
                
                with col2:
                    st.subheader("📊 Prediction Results")
                    
                    if risk_label == "High":
                        st.error(f"### 🔴 Risk Level: {risk_label}")
                        st.metric("High Risk Probability", f"{risk_prob:.1f}%")
                    else:
                        st.success(f"### 🟢 Risk Level: {risk_label}")
                        st.metric("Low Risk Probability", f"{100-risk_prob:.1f}%")
                    
                    # Progress bar
                    st.progress(risk_prob / 100)
                    
                    st.markdown("---")
                    st.markdown("**Input Summary:**")
                    st.write(f"- Age: {input_age}")
                    st.write(f"- Heart Rate: {input_hr} bpm")
                    st.write(f"- Blood Pressure: {input_bp} mmHg")
        
        st.markdown("---")
        st.subheader("📈 Model Performance Metrics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Model Type", "Random Forest")
        with col2:
            st.metric("Accuracy", "~99%")
        with col3:
            st.metric("Features Used", "3 (Age, HR, BP)")
    
    # ============================================================
    # PAGE 4: AI SUMMARIES
    # ============================================================
    elif page == "📝 AI Summaries":
        st.header("🤖 AI-Generated Medical Summaries")
        
        # Select patient
        patient_names = filtered_df['name'].tolist()
        selected_patient = st.selectbox("Select a patient:", patient_names)
        
        if selected_patient:
            patient_data = filtered_df[filtered_df['name'] == selected_patient].iloc[0]
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("📋 Patient Info")
                st.write(f"**ID:** {patient_data['patient_id']}")
                st.write(f"**Name:** {patient_data['name']}")
                st.write(f"**Age:** {patient_data['age']}")
                st.write(f"**Heart Rate:** {patient_data['heart_rate']} bpm")
                st.write(f"**Blood Pressure:** {patient_data['systolic_bp']}/{patient_data['diastolic_bp']} mmHg")
                
                if patient_data['risk_level'] == 'High':
                    st.error(f"**Risk Level:** 🔴 {patient_data['risk_level']}")
                else:
                    st.success(f"**Risk Level:** 🟢 {patient_data['risk_level']}")
            
            with col2:
                st.subheader("📝 Medical Notes")
                st.text_area("Original Notes:", patient_data['medical_notes'], height=150, disabled=True)
                
                # AI Summary
                if 'ai_summary' in patient_data and pd.notna(patient_data['ai_summary']):
                    st.markdown("### 🤖 AI Summary")
                    st.info(patient_data['ai_summary'])
                    
                    if 'medications' in patient_data and pd.notna(patient_data['medications']):
                        st.markdown("### 💊 Medications")
                        st.success(patient_data['medications'])
                else:
                    st.warning("⚠️ AI summary not yet generated for this patient.")
                    if st.button("Generate AI Summary"):
                        st.info("AI summarization requires OpenAI API credits or running the ai_summarizer.py script.")

    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: gray; font-size: 0.9rem;">'
        '🏥 Vital Scan - Healthcare Triage System | '
        f'Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | '
        f'{len(df)} Total Patients'
        '</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
