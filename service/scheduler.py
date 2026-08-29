from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
from enums import Frequency, MedicationStatus
from models import Medication, User
from service.email import send_completion_email, send_reminder_email

scheduler = BackgroundScheduler()


def get_reminder_times(frequency, reminder_time):
    """Generates scheduled hour triggers based on medication frequency."""
    if not reminder_time:
        return []

    if hasattr(reminder_time, "hour"):
        base_hour = reminder_time.hour
    else:
        base_hour = int(str(reminder_time).split(":")[0])

    if frequency == Frequency.once_daily:
        return [base_hour]
    elif frequency == Frequency.twice_daily:
        # Morning and evening (12-hour offset)
        return [base_hour, (base_hour + 12) % 24]
    elif frequency == Frequency.three_times_daily:
        # Morning, afternoon, evening (6-hour offsets)
        return [base_hour, (base_hour + 6) % 24, (base_hour + 12) % 24]

    return [base_hour]


def check_and_send_reminders():
    db = SessionLocal()
    try:
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute

        medications = (
            db.query(Medication)
            .filter(
                Medication.status == MedicationStatus.active,
                Medication.reminder_enabled == True,
            )
            .all()
        )

        for medication in medications:
            if medication.reminder_time is None:
                continue

            # Safely extract minute offset from reminder_time
            if hasattr(medication.reminder_time, "minute"):
                med_minute = medication.reminder_time.minute
            else:
                parts = str(medication.reminder_time).split(":")
                med_minute = int(parts[1]) if len(parts) > 1 else 0

            # Get target hours based on daily frequency
            target_hours = get_reminder_times(
                medication.frequency, medication.reminder_time
            )

            # Check if current hour matches any scheduled slots AND exact minute matches
            if current_hour in target_hours and current_minute == med_minute:
                user = (
                    db.query(User).filter(User.id == medication.user_id).first()
                )
                if user:
                    formatted_time = f"{current_hour:02d}:{med_minute:02d}"
                    send_reminder_email(
                        user_email=user.email,
                        username=user.username,
                        medication_name=medication.name,
                        dosage=medication.dosage,
                        reminder_time=formatted_time,
                    )
                    print(
                        f"Reminder sent to {user.email} for {medication.name} at {formatted_time}"
                    )

    except Exception as e:
        print(f"Reminder job failed: {e}")
    finally:
        db.close()


def check_and_complete_medications():
    db = SessionLocal()
    try:
        today = date.today()

        medications = (
            db.query(Medication)
            .filter(
                Medication.status == MedicationStatus.active,
                Medication.end_date <= today,
            )
            .all()
        )

        for medication in medications:
            medication.status = MedicationStatus.completed

            user = (
                db.query(User).filter(User.id == medication.user_id).first()
            )
            if user:
                send_completion_email(
                    user_email=user.email,
                    username=user.username,
                    medication_name=medication.name,
                )
                print(
                    f"Completion email sent to {user.email} for {medication.name}"
                )

        db.commit()

    except Exception as e:
        print(f"Completion job failed: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(check_and_send_reminders, "interval", minutes=1)
    scheduler.add_job(check_and_complete_medications, "cron", hour=0, minute=0)
    scheduler.start()
    print("Scheduler started")