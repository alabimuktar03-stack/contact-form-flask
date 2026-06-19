from flask import Flask, render_template, request
import smtplib
from email.message import EmailMessage
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

app = Flask(__name__)

# Email settings – read from environment variables
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'alabimuktar03@gmail.com')
APP_PASSWORD = os.environ.get('APP_PASSWORD', 'gxcv emlp mshn ysjz')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', 'alabimuktar03@gmail.com')

# Google Sheets setup (works both locally and on Render)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if 'GOOGLE_CREDS_JSON' in os.environ:
    # On Render: use the JSON string from environment variable
    creds_dict = json.loads(os.environ['GOOGLE_CREDS_JSON'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    # Local development: use the file
    creds = ServiceAccountCredentials.from_json_keyfile_name('my-key.json', scope)

client = gspread.authorize(creds)
sheet = client.open("Contact Form Leads").worksheet("Leads")

@app.route('/')
def show_form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def handle_submit():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    # 1. Send email (TLS on port 587)
    msg = EmailMessage()
    msg['Subject'] = f"New contact from {name}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg.set_content(f"Name: {name}\nEmail: {email}\nMessage: {message}")
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Email error: {e}")
    
    # 2. Add to Google Sheets
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, name, email, message])
        print("Google Sheet updated")
    except Exception as e:
        print(f"Sheets error: {e}")
    
    return "Thank you! We'll be in touch soon."

if __name__ == '__main__':
    app.run(debug=True)