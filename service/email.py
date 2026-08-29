import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from core.config import settings

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = settings.BREVO_API_KEY

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)

SENDER_EMAIL = "your_verified_gmail_here@gmail.com"  # ← your Brevo-verified email
SENDER_NAME = "D-Med Tracker"

def _send_email(to_email: str, subject: str, text_content: str):
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
        subject=subject,
        text_content=text_content,
    )
    try:
        api_instance.send_transac_email(send_smtp_email)
        print(f"Email sent to {to_email}")
    except ApiException as e:
        print(f"Brevo API error: {e}")


def send_reminder_email(user_email: str, username: str, medication_name: str, dosage: str, reminder_time: str):
    _send_email(
        to_email=user_email,
        subject=f"Medication Reminder — {medication_name}",
        text_content=f"""Hi {username},

This is a reminder to take your medication.

Medication: {medication_name}
Dosage: {dosage}
Scheduled time: {reminder_time}

Stay consistent — your health depends on it!

D-Med Tracker""",
    )


def send_completion_email(user_email: str, username: str, medication_name: str):
    _send_email(
        to_email=user_email,
        subject=f"Course Completed — {medication_name}",
        text_content=f"""Hi {username},

Congratulations! You have completed your medication course.

Medication: {medication_name}

Well done for staying consistent.

D-Med Tracker""",
    )


def send_welcome_email(user_email: str, username: str):
    _send_email(
        to_email=user_email,
        subject="Welcome to D-Med Tracker 💊",
        text_content=f"""Hi {username},

Welcome to D-Med Tracker!

You're all set to start tracking your medications and building healthy habits.

- Add your medications and dosage schedule
- Log when you take them daily
- Track your streak and stay consistent
- Get email reminders so you never miss a dose

Stay consistent — your health depends on it!

D-Med Tracker""",
    )
