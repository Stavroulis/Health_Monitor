import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
import base64
from fpdf import FPDF

st.set_page_config(page_title="Mobile Health Tracker", layout="centered")

st.markdown("""
    <link rel="manifest" href="manifest.json">
    <link rel="icon" href="your_favicon.png" sizes="192x192">
    <meta name="theme-color" content="#00aaff">
""", unsafe_allow_html=True)


st.markdown("""
    <link rel="icon" href="your_favicon.png" sizes="192x192">
    <style>
    .big-button button {
        font-size: 24px !important;
        padding: 1em 2em;
        border-radius: 1em;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <link rel="manifest" href="manifest.json">
    <style>
    .big-button button {
        font-size: 24px !important;
        padding: 1em 2em;
        border-radius: 1em;
    }
    </style>
""", unsafe_allow_html=True)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_patient_file(name):
    return os.path.join(DATA_DIR, f"{name}.csv")

def generate_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href

def generate_pdf_report(df, patient_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Health Report for {patient_name}", ln=True, align='C')
    pdf.ln(10)

    for index, row in df.tail(10).iterrows():
        pdf.cell(200, 10, txt=f"{row['Timestamp']} | Systolic: {row['Systolic']} | Diastolic: {row['Diastolic']} | Temp: {row['Temperature']}°C | Glucose: {row['Glucose']} | Vit D: {row['Vitamin D']}", ln=True)

    output_path = os.path.join(DATA_DIR, f"{patient_name}_report.pdf")
    pdf.output(output_path)
    return output_path

st.markdown("""
    <style>
    .big-button button {
        font-size: 24px !important;
        padding: 1em 2em;
        border-radius: 1em;
    }
    .stTextInput > div > div > input {
        font-size: 18px;
    }
    .stNumberInput > div > input {
        font-size: 18px;
    }
    .stSelectbox > div > div > div {
        font-size: 18px;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Health Tracker - Mobile")

st.subheader("Select or Add Patient")
patients = [f[:-4] for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
col1, col2 = st.columns([1, 2])

with col1:
    selected = st.selectbox("Select existing patient", ["Select"] + patients, label_visibility="collapsed")

with col2:
    new_name = st.text_input("Patient name input", placeholder="New patient name", label_visibility="collapsed")


if new_name:
    patient_name = new_name
elif selected != "Select":
    patient_name = selected
else:
    st.warning("Please select or enter a patient name")
    st.stop()

st.subheader(f"Patient: {patient_name}")

systolic = st.number_input("Systolic Pressure (mmHg)", min_value=80, max_value=200, value= 120, step=1)
diastolic = st.number_input("Diastolic Pressure (mmHg)", min_value=30, max_value=150, value=80, step=1)
temperature = st.number_input("Temperature (°C)", min_value=30.0, max_value=45.0,value=36.6, step=0.1)
glucose = st.number_input("Glucose (mg/dL)", min_value=40, max_value=500, value=100, step=1)
vitamin_d = st.number_input("Vitamin D (ng/mL)", min_value=0, max_value=150, value=20, step=1)

# Use current input values as reference lines
current_values = {
    "Systolic": systolic,
    "Diastolic": diastolic,
    "Temperature": temperature,
    "Glucose": glucose,
    "Vitamin D": vitamin_d
}

file_path = get_patient_file(patient_name)

if st.button("Save Entry", type="primary"):
    entry = {
        "Timestamp": datetime.now(),
        "Systolic": systolic,
        "Diastolic": diastolic,
        "Temperature": temperature,
        "Glucose": glucose,
        "Vitamin D": vitamin_d
    }
    df = pd.DataFrame([entry])
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)
    st.success("Data saved!")

if os.path.exists(file_path):
    st.subheader("View Data and Graphs")
    df = pd.read_csv(file_path, parse_dates=["Timestamp"])

    st.dataframe(df.tail(10))

    parameters = ["Systolic", "Diastolic", "Temperature", "Glucose", "Vitamin D"]

    # Two-column layout for charts
    chart_params = [
        ("Blood Pressure (mmHg)", ["Systolic", "Diastolic"]),
        ("Temperature (°C)", ["Temperature"]),
        ("Glucose (mg/dL)", ["Glucose"]),
        ("Vitamin D (ng/mL)", ["Vitamin D"])
    ]

    for i in range(0, len(chart_params), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(chart_params):
                title, params = chart_params[i + j]
                with cols[j]:
                    st.markdown(f"### {title}")
                    fig, ax = plt.subplots()
                    for param in params:
                        ax.plot(df["Timestamp"], df[param], marker='o', linestyle='-', label=param)

                        # Add horizontal line for current value
                        if param in current_values:
                            current_val = current_values[param]
                            ax.axhline(y=current_val, color='green', linestyle='--', linewidth=1, label=f'Current {param}')

                    ax.set_ylabel(title)
                    ax.set_xlabel("Date")
                    ax.legend()
                    plt.xticks(rotation=45)
                    st.pyplot(fig)

    st.markdown("### Export Data")
    st.markdown(generate_download_link(df, f"{patient_name}_data.csv"), unsafe_allow_html=True)

    if st.button("Generate PDF Report"):
        pdf_path = generate_pdf_report(df, patient_name)
        with open(pdf_path, "rb") as f:
            b64_pdf = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{patient_name}_report.pdf">Download PDF Report</a>'
            st.markdown(href, unsafe_allow_html=True)
