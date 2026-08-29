from datetime import date, datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
from enums import Frequency, MedicationStatus
from models import Medication, User
from service.email import send_completion_email, send_reminder_email

scheduler = BackgroundScheduler()

WAT = timezone(timedelta(hours=1))


def get_reminder_times(frequency, reminder_time):
    if not reminder_time:
        return []

    if hasattr(reminder_time, "hour"):
        base_hour = reminder_time.hour
    else:
        base_hour = int(str(reminder_time).split(":")[0])

    freq_str = frequency.value if hasattr(frequency, "value") else str(frequency)

    if freq_str == "once_daily":
        return [base_hour]
    elif freq_str == "twice_daily":
        return [base_hour, (base_hour + 12) % 24]
    elif freq_str == "three_times_daily":
        return [base_hour, (base_hour + 6) % 24, (base_hour + 12) % 24]

    return [base_hour]


def check_and_send_reminders():
    db = SessionLocal()
    sent_this_run = set()
    try:
        now = datetime.now(WAT)
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

            if hasattr(medication.reminder_time, "minute"):
                med_minute = medication.reminder_time.minute
            else:
                parts = str(medication.reminder_time).split(":")
                med_minute = int(parts[1]) if len(parts) > 1 else 0

            target_hours = get_reminder_times(
                medication.frequency, medication.reminder_time
            )

            # 2-minute window check
            if current_hour in target_hours and abs(current_minute - med_minute) <= 2:
                # Dedupe: skip if already sent this hour for this med+time combo
                send_key = f"{medication.id}_{medication.reminder_time}_{current_hour}"
                if send_key in sent_this_run:
                    continue
                sent_this_run.add(send_key)

                user = db.query(User).filter(User.id == medication.user_id).first()
                if user:
                    formatted_time = f"{medication.reminder_time.hour:02d}:{med_minute:02d}"
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
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def check_and_complete_medications():
    db = SessionLocal()
    try:
        today = datetime.now(WAT).date()

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
