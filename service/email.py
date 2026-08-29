import resend
from core.config import settings

resend.api_key = settings.RESEND_API_KEY


def send_reminder_email(user_email: str, username: str, medication_name: str, dosage: str, reminder_time: str):
    resend.Emails.send({
        "from": "D-Med Tracker <onboarding@resend.dev>",
        "to": user_email,
        "subject": f"Medication Reminder — {medication_name}",
        "text": f"""Hi {username},

This is a reminder to take your medication.

Medication: {medication_name}
Dosage: {dosage}
Scheduled time: {reminder_time}

Stay consistent — your health depends on it!

D-Med Tracker"""
    })
    print(f"Reminder email sent to {user_email}")


def send_completion_email(user_email: str, username: str, medication_name: str):
    resend.Emails.send({
        "from": "D-Med Tracker <onboarding@resend.dev>",
        "to": user_email,
        "subject": f"Course Completed — {medication_name}",
        "text": f"""Hi {username},

Congratulations! You have completed your medication course.

Medication: {medication_name}

Well done for staying consistent.

D-Med Tracker"""
    })
    print(f"Completion email sent to {user_email}")


def send_welcome_email(user_email: str, username: str):
    resend.Emails.send({
        "from": "D-Med Tracker <onboarding@resend.dev>",
        "to": user_email,
        "subject": "Welcome to D-Med Tracker 💊",
        "text": f"""Hi {username},

Welcome to D-Med Tracker!

You're all set to start tracking your medications and building healthy habits.

Here's what you can do:
- Add your medications and dosage schedule
- Log when you take them daily
- Track your streak and stay consistent
- Get email reminders so you never miss a dose

Stay consistent — your health depends on it!

D-Med Tracker"""
    })
    print(f"Welcome email sent to {user_email}")