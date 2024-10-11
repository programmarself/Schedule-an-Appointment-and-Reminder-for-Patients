import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Function to generate random appointments for a week for multiple patients
def generate_appointments(num_patients=5, num_days=7, appointment_duration=30, time_interval=15):
    patient_ids = [f'Patient_{i:03d}' for i in range(1, num_patients + 1)]
    dates = [datetime.now().date() + timedelta(days=i) for i in range(num_days)]
    times = [datetime.strptime(f"{hour:02d}:{minute:02d} {AM_PM}", "%H:%M %p") for hour in range(9, 17, time_interval) for AM_PM in ["AM", "PM"]]
    appointments = []

    for patient_id in patient_ids:
        for date in dates:
            for time in times:
                start_time = time
                end_time = start_time + timedelta(minutes=appointment_duration)
                appointments.append([patient_id, date, start_time, end_time])

    df_appointments = pd.DataFrame(appointments, columns=['Patient ID', 'Date', 'Start Time', 'End Time'])

    return df_appointments

# Function to identify scheduling conflicts within the generated appointments
def detect_conflicts(appointments_df):
    conflicts = appointments_df[appointments_df.duplicated(subset=['Date', 'Start Time', 'End Time'], keep=False)]
    return conflicts

# Function to generate reminders for appointments scheduled for the next day
def generate_reminders(appointments_df):
    tomorrow_date = datetime.now().date() + timedelta(days=1)
    reminders = appointments_df[appointments_df['Date'] == tomorrow_date]
    reminder_messages = []
    for _, row in reminders.iterrows():
        message = f"Reminder: You have an appointment scheduled on {row['Date']} at {row['Start Time']}. Please arrive 10 minutes early."
        reminder_messages.append((row['Patient ID'], message))
    return reminder_messages

# Function to cancel an appointment
def cancel_appointment(appointment_id, appointments_df):
    appointments_df = appointments_df[appointments_df['Appointment ID'] != appointment_id]
    return appointments_df

# Function to reschedule an appointment
def reschedule_appointment(appointment_id, new_date, new_start_time, appointments_df):
    appointments_df.loc[appointments_df['Appointment ID'] == appointment_id, 'Date'] = new_date
    appointments_df.loc[appointments_df['Appointment ID'] == appointment_id, 'Start Time'] = new_start_time
    # Calculate new end time based on appointment duration
    appointments_df.loc[appointments_df['Appointment ID'] == appointment_id, 'End Time'] = new_start_time + timedelta(minutes=appointments_df.loc[appointments_df['Appointment ID'] == appointment_id, 'Duration'].iloc[0])
    return appointments_df

# Function to send reminders via email or SMS
import smtplib
from email.mime.text import MIMEText

def send_reminder(patient_id, appointment_date, appointment_time, email_address, phone_number):
    message = f"Reminder: You have an appointment on {appointment_date} at {appointment_time}."
    
    # Sending email (example with SMTP)
    msg = MIMEText(message)
    msg['Subject'] = 'Appointment Reminder'
    msg['From'] = 'your_email@example.com'
    msg['To'] = email_address
    
    with smtplib.SMTP('smtp.example.com') as server:
        server.login('your_email@example.com', 'your_password')
        server.sendmail('your_email@example.com', [email_address], msg.as_string())
    
    # Placeholder for SMS sending logic
    print(f"SMS to {phone_number}: {message}")
    # Implementation for sending email or SMS using appropriate libraries
    # ...

# Streamlit App

st.title("Appointment Management System")

# User Input for Appointments
with st.expander("Generate Appointments"):
    num_patients = st.number_input("Number of Patients:", min_value=1, value=5)
    num_days = st.number_input("Number of Days:", min_value=1, value=7)
    appointment_duration = st.slider("Appointment Duration (minutes):", min_value=15, max_value=60, value=30)
    time_intervals = st.selectbox("Time Intervals:", options=["15 minutes", "30 minutes", "60 minutes"])

    generate_button = st.button("Generate Appointments")

if generate_button:
    appointments_df = generate_appointments(num_patients, num_days, appointment_duration, time_intervals)
    appointments_df['Appointment ID'] = range(1, len(appointments_df) + 1)
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

# Appointment Cancellation
with st.expander("Cancel Appointment"):
    appointment_id = st.number_input("Appointment ID:")
    cancel_button = st.button("Cancel")

    if cancel_button:
        appointments_df = cancel_appointment(appointment_id, appointments_df.copy())
        st.success("Appointment canceled successfully!")

# Appointment Rescheduling
with st.expander("Reschedule Appointment"):
    appointment_id = st.number_input("Appointment ID:")
    new_date = st.date_input("New Date:")
    new_start_time = st.time_input("New Start Time:")
    reschedule_button = st.button("Reschedule")

    if reschedule_button:
        appointments_df = reschedule_appointment(appointment_id, new_date, new_start_time, appointments_df.copy())
        st.success("Appointment rescheduled successfully!")

# Send Reminders (based on user preferences)
send_reminders_checkbox = st.checkbox("Send Reminders")
if send_reminders_checkbox:
    # ... (implementation for sending reminders)
