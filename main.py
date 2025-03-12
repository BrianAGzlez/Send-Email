import streamlit as st
import pandas as pd
import os
import time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To

def send_emails(api_key, sender_email, df, subject, body_template):
    sg = SendGridAPIClient(api_key)
    
    for _, row in df.iterrows():
        first_name = row["first_name"]
        last_name = row["last_name"]
        recipient_email = row["email"]
        
        body = body_template.replace("{first_name}", first_name).replace("{last_name}", last_name)
        
        # Corrección: Usar To() para los destinatarios
        message = Mail(
            from_email=sender_email,
            to_emails=To(recipient_email),  # ← SOLUCIÓN AQUÍ
            subject=subject,
            plain_text_content=body
        )
        
        try:
            response = sg.send(message)
            toast = st.empty()
            toast.success(f"✅ Email sent to {first_name} {last_name} ({recipient_email}) - Status: {response.status_code}")
            time.sleep(2)
            toast.empty()
        except Exception as e:
            toast = st.empty()
            toast.error(f"❌ Error sending email to {recipient_email}: {str(e)}")
            time.sleep(2)
            toast.empty()
            st.error(f"❌ Full error for {recipient_email}: {str(e)}")

# Configuración de la interfaz de Streamlit
st.set_page_config(page_title="Bulk Email Sender", page_icon="📧", layout="centered")

st.title("📧 Bulk Email Sender with SendGrid")
st.markdown("Upload an Excel or CSV file, customize your message, and send emails easily.")

# Subir archivo
uploaded_file = st.file_uploader("📂 Upload Excel or CSV file", type=["xlsx", "csv"], help="Make sure the file contains 'first_name', 'last_name', and 'email' columns.")

# Datos del usuario
sender_email = st.text_input("✉️ Your Email (Sender)", placeholder="your_email@example.com")
sendgrid_api_key = st.text_input("🔑 SendGrid API Key", type="password", placeholder="Enter your API Key")

# Personalización del correo
subject = st.text_input("📌 Email Subject", value="Arkham Exchange - Account Onboarding")
default_body = """
Dear {first_name} {last_name},

Arkham Exchange is now permitting residents of your region to onboard.
You can now complete your application here: https://auth.arkm.com/register

Best Regards, 
Arkham Team
"""
body_template = st.text_area("✉️ Email Body", value=default_body, height=200)

# Validación y envío
if uploaded_file and sender_email and sendgrid_api_key:
    file_extension = os.path.splitext(uploaded_file.name)[-1].lower()
    df = pd.read_excel(uploaded_file) if file_extension == ".xlsx" else pd.read_csv(uploaded_file)
    
    if all(col in df.columns for col in ["first_name", "last_name", "email"]):
        if st.button("🚀 Send Emails", help="Click to start sending emails"):
            send_emails(sendgrid_api_key, sender_email, df, subject, body_template)
    else:
        st.error("⚠️ The file must contain 'first_name', 'last_name', and 'email' columns.")
