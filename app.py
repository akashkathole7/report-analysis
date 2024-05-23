import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import traceback
import logging
import os

# Create the 'uploads' directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

st.title(" Alert System")

# Form inputs
email = st.text_input("Email")
password = st.text_input("Password", type="password")
suspect_file = st.file_uploader("Upload Suspect File", type=["csv"])
police_station_file = st.file_uploader("Upload Police Station File", type=["csv"])

if st.button("Send Alerts"):
    if not suspect_file or not police_station_file or not email or not password:
        st.error("Please fill out all fields and upload both files.")
    else:
        try:
            # Save uploaded CSV files
            suspect_file_path = os.path.join(UPLOAD_FOLDER, 'suspect_details.csv')
            police_station_file_path = os.path.join(UPLOAD_FOLDER, 'police_station_details.csv')

            with open(suspect_file_path, "wb") as f:
                f.write(suspect_file.getbuffer())

            with open(police_station_file_path, "wb") as f:
                f.write(police_station_file.getbuffer())

            # Load suspect details from CSV
            suspect_data = pd.read_csv(suspect_file_path)

            # Load police station details from CSV
            police_station_data = pd.read_csv(police_station_file_path)

            # Email configuration
            login_acc = email
            login_pass = password

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(login_acc, login_pass)

            # Iterate through suspect details
            for index, suspect in suspect_data.iterrows():
                # Extract suspect information
                first_name = suspect['first_name']
                middle_name = suspect['middle_name']
                surname = suspect['surname']
                phone = suspect['phone']
                email = suspect['email']
                address = suspect['address']
                dob = suspect['date_of_birth']
                pincode = suspect['pincode']

                # Find matching police station details based on pincode
                matching_police_station = police_station_data.loc[police_station_data['pincode'] == pincode]

                # If matching police station found
                if not matching_police_station.empty:
                    # Prepare email message
                    msg = MIMEMultipart()
                    msg['From'] = login_acc
                    msg['Subject'] = "Suspect Alert: " + first_name + " " + surname

                    # Construct email body
                    email_body = f"Suspect details:\nName: {first_name} {middle_name} {surname}\nPhone: {phone}\nEmail: {email}\nAddress: {address}\nDate of Birth: {dob}\nPincode: {pincode}\n"
                    msg.attach(MIMEText(email_body, 'plain'))

                    # Send email to matching police station
                    for _, station in matching_police_station.iterrows():
                        police_station_email = station['email']
                        msg['To'] = police_station_email
                        server.sendmail(login_acc, police_station_email, msg.as_string())
                        st.write(f"Email sent to {police_station_email} regarding suspect: {first_name} {surname}")

            # Quit SMTP server
            server.quit()
            st.success("Alerts sent successfully.")

        except Exception as e:
            logging.error(traceback.format_exc())
            st.error(f"An error occurred: {str(e)}")
