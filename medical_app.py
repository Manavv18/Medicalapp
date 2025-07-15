import streamlit as st
import pandas as pd
import pickle
import base64
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="AI Medical Triage System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
/* Main background and theme */
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
}

/* Custom header styling */
.header-container {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
    text-align: center;
}

.main-title {
    font-size: 3rem;
    font-weight: bold;
    color: white;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.sub-title {
    font-size: 1.2rem;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 1rem;
}

/* Input container styling */
.input-container {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Result cards */
.result-card {
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    text-align: center;
    font-size: 1.2rem;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    animation: fadeIn 0.5s ease-in;
}

.high-urgency {
    background: linear-gradient(135deg, #ff6b6b, #ff5252);
    color: white;
}

.medium-urgency {
    background: linear-gradient(135deg, #ffa726, #ff9800);
    color: white;
}

.low-urgency {
    background: linear-gradient(135deg, #66bb6a, #4caf50);
    color: white;
}

/* Loading animation */
.loading {
    text-align: center;
    padding: 2rem;
}

.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Info cards */
.info-card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
    border-left: 4px solid #3498db;
}

.warning-card {
    background: rgba(255, 193, 7, 0.1);
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
    border-left: 4px solid #ffc107;
}
</style>
""", unsafe_allow_html=True)

# Rule-based emergency classification
def rule_based_classification(age, heart_rate, systolic_bp, diastolic_bp, temperature, primary_symptom):
    """Emergency rule-based classification for medical triage"""
    score = 0
    
    # Age factor
    if age >= 65:
        score += 2
    elif age >= 45:
        score += 1
    
    # Heart rate assessment
    if heart_rate > 120 or heart_rate < 50:
        score += 3
    elif heart_rate > 100 or heart_rate < 60:
        score += 1
    
    # Blood pressure assessment
    if systolic_bp < 90 or systolic_bp > 180:
        score += 3
    elif systolic_bp < 100 or systolic_bp > 140:
        score += 1
    
    if diastolic_bp < 60 or diastolic_bp > 110:
        score += 2
    elif diastolic_bp > 90:
        score += 1
    
    # Temperature assessment
    if temperature >= 40.0 or temperature <= 35.0:
        score += 3
    elif temperature >= 38.5 or temperature <= 35.5:
        score += 2
    elif temperature >= 37.5:
        score += 1
    
    # Critical symptoms
    critical_symptoms = ["chest_pain", "shortness_of_breath", "dizziness"]
    severe_symptoms = ["abdominal_pain", "fever", "headache"]
    
    if primary_symptom in critical_symptoms:
        score += 3
    elif primary_symptom in severe_symptoms:
        score += 2
    elif primary_symptom != "none":
        score += 1
    
    # Classification based on score
    if score >= 7:
        return "High"
    elif score >= 4:
        return "Medium"
    else:
        return "Low"

# Header
st.markdown("""
<div class="header-container">
    <div class="main-title">🏥 AI Medical Triage System</div>
    <div class="sub-title">Intelligent Patient Screening & Urgency Assessment</div>
    <div style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">
        Powered by Advanced Machine Learning • Real-time Analysis
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 System Information")
    
    st.markdown("""
    <div class="info-card">
        <strong>🎯 Purpose:</strong><br>
        This AI system helps medical staff prioritize patient care based on vital signs and symptoms.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <strong>🔍 How it works:</strong><br>
        • Input patient vital signs<br>
        • Select primary symptom<br>
        • AI analyzes the data<br>
        • Provides urgency level
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🚨 Urgency Levels")
    
    st.markdown("""
    <div style="background: #ff6b6b; color: white; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0;">
        <strong>🟥 HIGH</strong><br>
        Immediate attention required
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #ffa726; color: white; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0;">
        <strong>🟧 MEDIUM</strong><br>
        Prompt care needed
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #66bb6a; color: white; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0;">
        <strong>🟩 LOW</strong><br>
        Routine care acceptable
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚠️ Important Notice")
    st.markdown("""
    <div class="warning-card">
        This system is for screening purposes only. Always consult with medical professionals for final diagnosis and treatment decisions.
    </div>
    """, unsafe_allow_html=True)

# Load model
model_loaded = False
model = None
try:
    with open("triage_model.pkl", "rb") as f:
        model = pickle.load(f)
    model_loaded = True
    st.success("✅ Model loaded successfully!")
except FileNotFoundError:
    st.warning("⚠️ **Model file not found.** Using rule-based emergency classification for demonstration.")
    model_loaded = False

# Input form
st.markdown("### 📝 Patient Information Input")
st.markdown('<div class="input-container">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 👤 Patient Demographics")
    age = st.number_input("Age (years)", min_value=0, max_value=120, value=30, help="Patient's age in years")
    
    st.markdown("#### 🌡️ Temperature")
    temperature = st.number_input("Body Temperature (°C)", min_value=30.0, max_value=43.0, value=36.5, step=0.1, help="Normal range: 36.1-37.2°C")

with col2:
    st.markdown("#### 💓 Vital Signs")
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, value=80, help="Normal range: 60-100 bpm")
    
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        systolic_bp = st.number_input("Systolic BP (mmHg)", min_value=70, max_value=250, value=120, help="Normal: < 120 mmHg")
    with col2_2:
        diastolic_bp = st.number_input("Diastolic BP (mmHg)", min_value=40, max_value=150, value=80, help="Normal: < 80 mmHg")

st.markdown("#### 🩺 Primary Symptom")
symptoms = [
    "none", "abdominal_pain", "chest_pain", "dizziness", "fever",
    "headache", "shortness_of_breath", "cough", "diarrhea", "nausea", "vomiting"
]

symptom_display = {
    "none": "No specific symptoms",
    "abdominal_pain": "Abdominal Pain",
    "chest_pain": "Chest Pain",
    "dizziness": "Dizziness",
    "fever": "Fever",
    "headache": "Headache",
    "shortness_of_breath": "Shortness of Breath",
    "cough": "Cough",
    "diarrhea": "Diarrhea",
    "nausea": "Nausea",
    "vomiting": "Vomiting"
}

primary_symptom = st.selectbox(
    "Select the most prominent symptom",
    symptoms,
    format_func=lambda x: symptom_display[x],
    help="Choose the primary complaint or symptom"
)

st.markdown('</div>', unsafe_allow_html=True)

# Prepare input data
input_dict = {
    "Age": age,
    "HeartRate": heart_rate,
    "SystolicBP": systolic_bp,
    "DiastolicBP": diastolic_bp,
    "Temperature": temperature
}

for sym in symptoms:
    input_dict[f"PrimarySymptom_{sym}"] = 1 if primary_symptom == sym else 0

input_df = pd.DataFrame([input_dict])

# Prediction section
st.markdown("### 🔍 Urgency Assessment")

# Predict button
if st.button("🚀 Analyze Patient Urgency", key="predict_btn"):
    # Show loading
    loading_placeholder = st.empty()
    loading_placeholder.markdown("""
    <div class="loading">
        <div class="spinner"></div>
        <p style="margin-top: 1rem; color: #666;">Analyzing patient data...</p>
    </div>
    """, unsafe_allow_html=True)
    
    time.sleep(2)
    
    # Make prediction
    if model_loaded:
        try:
            # Debug information
            st.markdown("#### 🔍 Debug Information")
            with st.expander("View Input Data"):
                st.dataframe(input_df)
                st.write(f"**Model Features Expected:** {list(model.feature_names_in_)}")
                st.write(f"**Input Features Provided:** {list(input_df.columns)}")
            
            # Reorder features
            input_df_ordered = input_df[model.feature_names_in_]
            
            # Predict
            prediction = model.predict(input_df_ordered)[0]
            
            # Get probabilities if available
            try:
                prediction_proba = model.predict_proba(input_df_ordered)[0]
                st.write(f"**Model Prediction Probabilities:** {dict(zip(model.classes_, prediction_proba))}")
            except:
                pass
            
            # Rule-based backup
            rule_prediction = rule_based_classification(age, heart_rate, systolic_bp, diastolic_bp, temperature, primary_symptom)
            
            st.write(f"**ML Model Prediction:** {prediction}")
            st.write(f"**Rule-based Prediction:** {rule_prediction}")
            
            # Check for mismatch
            if prediction != rule_prediction:
                st.warning(f"⚠️ **Prediction Mismatch:** Model says '{prediction}' but rule-based system suggests '{rule_prediction}'")
                if rule_prediction == "High":
                    st.error("🚨 **Override Recommended:** Clinical signs suggest HIGH urgency regardless of model prediction!")
                    final_prediction = rule_prediction
                else:
                    final_prediction = prediction
            else:
                final_prediction = prediction
                
        except Exception as e:
            st.error(f"❌ **Model Prediction Failed:** {str(e)}")
            st.info("🔄 **Falling back to rule-based classification...**")
            final_prediction = rule_based_classification(age, heart_rate, systolic_bp, diastolic_bp, temperature, primary_symptom)
    else:
        final_prediction = rule_based_classification(age, heart_rate, systolic_bp, diastolic_bp, temperature, primary_symptom)
    
    # Clear loading
    loading_placeholder.empty()
    
    # Show results
    st.markdown("### 📋 Assessment Results")
    
    if final_prediction == "High":
        st.markdown("""
        <div class="result-card high-urgency">
            🚨 HIGH URGENCY DETECTED<br>
            <div style="font-size: 1rem; margin-top: 0.5rem;">
                Immediate medical attention required!<br>
                Patient should be seen immediately.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.error("🔴 **PRIORITY ALERT:** This patient requires immediate medical evaluation and treatment.")
        
    elif final_prediction == "Medium":
        st.markdown("""
        <div class="result-card medium-urgency">
            ⚠️ MEDIUM URGENCY<br>
            <div style="font-size: 1rem; margin-top: 0.5rem;">
                Prompt care needed, but not life-threatening.<br>
                Patient should be seen within 1-2 hours.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.warning("🟠 **MODERATE PRIORITY:** Patient needs timely medical attention but condition is not critical.")
        
    else:  # Low
        st.markdown("""
        <div class="result-card low-urgency">
            ✅ LOW URGENCY<br>
            <div style="font-size: 1rem; margin-top: 0.5rem;">
                Routine care or self-care is acceptable.<br>
                Patient can wait for standard appointment.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.success("🟢 **ROUTINE CARE:** Patient can be scheduled for regular consultation or self-care measures.")
    
    # Additional metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Patient Age", f"{age} years")
    with col2:
        st.metric("Heart Rate", f"{heart_rate} bpm")
    with col3:
        st.metric("Temperature", f"{temperature}°C")
    
    st.markdown(f"*Assessment completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")