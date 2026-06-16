from flask import Flask, render_template, request
import smtplib
from email.message import EmailMessage
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# Email settings
SENDER_EMAIL = "your-email@gmail.com"
APP_PASSWORD = "xxxx xxxx xxxx xxxx"
RECIPIENT_EMAIL = "business-owner@example.com"

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Replace 'path/to/your-downloaded-key.json' with the actual path to the JSON file you downloaded
creds = ServiceAccountCredentials.from_json_keyfile_name('my-key.json', scope)
client = gspread.authorize(creds)

# Open your sheet by name (must match exactly)
sheet = client.open("Contact Form Leads").worksheet("Leads")

@app.route('/')
def show_form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def handle_submit():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    # 1. Send email (same as before)
    msg = EmailMessage()
    msg['Subject'] = f"New contact from {name}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg.set_content(f"Name: {name}\nEmail: {email}\nMessage: {message}")
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
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

