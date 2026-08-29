from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date
from database import SessionLocal
from models import Medication, User
from enums import MedicationStatus
from service.email import send_reminder_email, send_completion_email

scheduler = BackgroundScheduler()


def check_and_send_reminders():
    db = SessionLocal()
    try:
        current_hour = datetime.now().hour

        
        medications = db.query(Medication).filter(
            Medication.status == MedicationStatus.active,
            Medication.reminder_enabled == True
        ).all()

        for medication in medications:
            if medication.reminder_time is None:
                continue

            
            if medication.reminder_time.hour == current_hour:
                user = db.query(User).filter(User.id == medication.user_id).first()
                if user:
                    send_reminder_email(
                        user_email=user.email,
                        username=user.username,
                        medication_name=medication.name,
                        dosage=medication.dosage,
                        reminder_time=medication.reminder_time
                    )
                    print(f"Reminder sent to {user.email} for {medication.name}")

    except Exception as e:
        print(f"Reminder job failed: {e}")
    finally:
        db.close()


def check_and_complete_medications():
    db = SessionLocal()
    try:
        today = date.today()

        
        medications = db.query(Medication).filter(
            Medication.status == MedicationStatus.active,
            Medication.end_date <= today
        ).all()

        for medication in medications:
            
            medication.status = MedicationStatus.completed

            user = db.query(User).filter(User.id == medication.user_id).first()
            if user:
                send_completion_email(
                    user_email=user.email,
                    username=user.username,
                    medication_name=medication.name
                )
                print(f"Completion email sent to {user.email} for {medication.name}")

        db.commit()

    except Exception as e:
        print(f"Completion job failed: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(check_and_send_reminders, 'interval', minutes=1)
    scheduler.add_job(check_and_complete_medications, 'cron', hour=0, minute=0)
    scheduler.start()
    print("Scheduler started")
    