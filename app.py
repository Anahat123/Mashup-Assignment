from flask import Flask, render_template, request
import zipfile
import re
import smtplib
from email.message import EmailMessage
import importlib.util
import os

app = Flask(__name__)

# Dynamically import 102313058.py
spec = importlib.util.spec_from_file_location("mashup_module", "102313058.py")
mashup_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mashup_module)


# Email validation
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        singer = request.form['singer']
        number = int(request.form['number'])
        duration = int(request.form['duration'])
        email = request.form['email']

        if number <= 10 or duration <= 20:
            return "Number must be >10 and duration >20"

        if not is_valid_email(email):
            return "Invalid email address"

        output_file = "mashup.mp3"

        try:
            # Call function from 102313058.py
            mashup_module.create_mashup(singer, number, duration, output_file)

            # Create zip file
            zip_filename = "mashup.zip"
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                zipf.write(output_file)

            send_email(email, zip_filename)

            return "Mashup created and emailed successfully!"

        except Exception as e:
            return f"Error occurred: {e}"

    return render_template('index.html')


def send_email(receiver_email, filename):
    sender_email = os.environ.get("EMAIL_USER")
    sender_password = os.environ.get("EMAIL_PASS")


    msg = EmailMessage()
    msg['Subject'] = "Your Mashup File"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content("Your mashup is attached.")

    with open(filename, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype='application', subtype='zip', filename=filename)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)


if __name__ == '__main__':
    app.run(debug=True)
