import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from core.config import settings


def _dispatch_email(to_email: str, subject: str, body_text: str):
    """Internal helper to construct and send email via Gmail SMTP."""
    message = MIMEMultipart()
    message["From"] = formataddr(("D-Med Tracker", settings.SENDER_EMAIL))
    message["To"] = to_email.strip()
    message["Subject"] = subject
    message.attach(MIMEText(body_text, "plain"))

    try:
        print(f"Connecting to SMTP server for {to_email}...")

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.starttls()
            server.login(settings.SENDER_EMAIL, settings.GMAIL_PASSWORD)
            server.sendmail(
                settings.SENDER_EMAIL,
                to_email.strip(),
                message.as_string()
            )

        print(f"Email sent successfully to {to_email}")

    except smtplib.SMTPAuthenticationError as auth_err:
        print(f"SMTP Auth Error: {auth_err}")
        raise

    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")
        raise

    
def send_reminder_email(user_email, username, medication_name, dosage, reminder_time):
    subject = f"Medication Reminder — {medication_name}"
    body_text = (
        f"Hi {username},\n\n"
        f"This is a reminder to take your medication.\n"
        f"Medication: {medication_name}\n"
        f"Dosage: {dosage}\n"
        f"Scheduled time: {reminder_time}\n"
        f"Stay consistent — your health depends on it!\n\n"
        f"D-Med Tracker"
    )
    _dispatch_email(user_email, subject, body_text)


def send_completion_email(user_email, username, medication_name):
    subject = f"Course Completed — {medication_name}"
    body_text = (
        f"Hi {username},\n\n"
        f"Congratulations! You have completed your medication course.\n"
        f"Medication: {medication_name}\n"
        f"Well done for staying consistent.\n\n"
        f"D-Med Tracker"
    )
    _dispatch_email(user_email, subject, body_text)


def send_welcome_email(user_email: str, username: str):
    subject = "Welcome to D-Med Tracker 💊"
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
    _dispatch_email(user_email, subject, body_text)