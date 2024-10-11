import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Function to generate random appointments for a week for multiple patients
def generate_appointments(num_patients=5, num_days=7):
    patient_ids = [f'Patient_{i:03d}' for i in range(1, num_patients + 1)]
    dates = [datetime.now().date() + timedelta(days=i) for i in range(num_days)]
    times = ['09:00 AM', '11:00 AM', '02:00 PM', '04:00 PM']
    appointments = []

    for patient_id in patient_ids:
        for date in dates:
            time = np.random.choice(times)
            appointments.append([patient_id, date, time])

    df_appointments = pd.DataFrame(appointments, columns=['Patient ID', 'Date', 'Time'])

    return df_appointments

# Function to identify scheduling conflicts within the generated appointments
def detect_conflicts(appointments_df):
    conflicts = appointments_df[appointments_df.duplicated(subset=['Date', 'Time'], keep=False)]
    return conflicts

# Function to generate reminders for appointments scheduled for the next day
def generate_reminders(appointments_df, reminder_template="Reminder: You have an appointment scheduled on {date} at {time}. Please arrive 10 minutes early."):
    """
    Generate reminders for appointments scheduled for the next day.
    
    Parameters:
    appointments_df (pd.DataFrame): DataFrame containing appointment information.
    reminder_template (str): Template for the reminder message. Default is a standard reminder message.
    
    Returns:
    list: List of tuples containing patient ID and reminder message.
    """
    tomorrow_date = datetime.now().date() + timedelta(days=1)
    reminders = appointments_df[appointments_df['Date'] == tomorrow_date]
    
    reminder_messages = [
        (row['Patient ID'], reminder_template.format(date=row['Date'], time=row['Time']))
        for _, row in reminders.iterrows()
    ]
    
    return reminder_messages 

# Streamlit App

st.title("Appointment Management System")

# User Input for Appointments
with st.expander("Generate Appointments"):
    num_patients = st.number_input("Number of Patients:", min_value=1, value=5)
    num_days = st.number_input("Number of Days:", min_value=1, value=7)
    generate_button = st.button("Generate Appointments")

if generate_button:
    appointments_df = generate_appointments(num_patients, num_days)
    st.subheader("Generated Appointments:")
    st.dataframe(appointments_df)

    conflicts = detect_conflicts(appointments_df.copy())
    if not conflicts.empty:
        st.subheader("Scheduling Conflicts Detected:")
        st.dataframe(conflicts)
    else:
        st.success("No scheduling conflicts found!")

    reminders = generate_reminders(appointments_df.copy())
    if not reminders:
        st.info("No appointments scheduled for tomorrow.")
    else:
        st.subheader("Appointment Reminders for Tomorrow:")
        for patient_id, message in reminders:
            st.write(f"{patient_id}: {message}")
