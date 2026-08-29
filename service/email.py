from core.config import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr


def send_reminder_email(user_email, username, medication_name, dosage, reminder_time):
    message = MIMEMultipart()
    formataddr(("D-Med Tracker", settings.SENDER_EMAIL))
    message["To"] = user_email.strip()
    message["Subject"] = f"Medication Reminder — {medication_name}"

    body_text = f"Hi {username}, \n \n This is a reminder to take your medication. \n Medication: {medication_name} \n Dosage: {dosage} \n Scheduled time: {reminder_time} \n Stay consistent — your health depends on it! \n \n D Medication Tracker"
    message.attach(MIMEText(body_text, "plain"))

    try:
        print("Connecting to SMTP server.....")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()

            server.login(settings.SENDER_EMAIL, settings.GMAIL_PASSWORD)

            server.sendmail(settings.SENDER_EMAIL, user_email, message.as_string())

        print("Email Sent successfully")

    except Exception as e:
        print(f"Failed to send email. Error: {e}")



def send_completion_email(user_email, username, medication_name):
    message = MIMEMultipart()
    formataddr(("D-Med Tracker", settings.SENDER_EMAIL))
    message["To"] = user_email.strip()
    message["Subject"] = f"Course Completed — {medication_name}"

    body_text = f"Hi {username}, \n \n Congratulations! You have completed your medication course. \n Medication: {medication_name} \n Well done for staying consistent.  \n \n D Medication Tracker"
    message.attach(MIMEText(body_text, "plain"))

    try:
        print("Connecting to SMTP server.....")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()

            server.login(settings.SENDER_EMAIL, settings.GMAIL_PASSWORD)

            server.sendmail(settings.SENDER_EMAIL, user_email, message.as_string())

        print("Email Sent successfully")

    except Exception as e:
        print(f"Failed to send email. Error: {e}")
    



def send_welcome_email(user_email: str, username: str):
    message = MIMEMultipart()
    message["From"] = formataddr(("D-Med Tracker", settings.SENDER_EMAIL))
    message["To"] = user_email.strip()
    message["Subject"] = "Welcome to D-Med Tracker 💊"

    body_text = f"""Hi {username},

        Welcome to D-Med Tracker!

        You're all set to start tracking your medications and building healthy habits.

        Here's what you can do:
        - Add your medications and dosage schedule
        - Log when you take them daily
        - Track your streak and stay consistent
        - Get email reminders so you never miss a dose

        Stay consistent — your health depends on it!

        D-Med Tracker
        """
    message.attach(MIMEText(body_text, "plain"))

    try:
        print("Connecting to SMTP server.....")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(settings.SENDER_EMAIL, settings.GMAIL_PASSWORD)
            server.sendmail(settings.SENDER_EMAIL, user_email, message.as_string())
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")