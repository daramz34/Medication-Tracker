from sqlalchemy.orm import Session
from models import User, Medication, MedicationLog, Streak
from enums import LogStatus,MedicationStatus
from schemas import (LogCreate,MedicatedUpdate, 
                                        UserCreate,MedicationCreate)
from core.security import verify_password, hashed_password
from datetime import date, timedelta
from models import utcnow
def get_user_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
def get_user_emal(db:Session, email:str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db:Session, username:str, password: str):
    db_user = get_user_username(db, username)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user

def create_user(db:Session, user:UserCreate):
    db_user = User(**user.model_dump(exclude={"password"}),
                   hashed_password = hashed_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def create_medication(db:Session, medication: MedicationCreate, current_user: User):
    end_date = medication.start_date + timedelta(days=medication.duration_days)
    med_data = medication.model_dump()
    med_data["end_date"] = end_date
    db_med = Medication(**med_data,
                        user_id = current_user.id,)
    db.add(db_med)
    db.commit()
    db.refresh(db_med)

    get_or_create_streak(db, db_med.id, current_user.id)
    return db_med

def get_all_medications(db:Session, current_user:User):
    db_med = db.query(Medication).filter(Medication.user_id == current_user.id).all()
    if not db_med:
        return None
    return db_med
def get_medications_by_id(db:Session, med_id: int, current_user:User):
    db_med = db.query(Medication).filter(Medication.id == med_id,
                                         Medication.user_id == current_user.id).first()
    if not db_med:
        return None
    return db_med

def update_medication(db: Session, med_id: int, update:MedicatedUpdate, current_user:User):
    db_med = db.query(Medication).filter(Medication.id == med_id,
                                         Medication.user_id == current_user.id).first()
    if not db_med:
        return None

    db_update = update.model_dump(exclude_none=True)
    for key, value in db_update.items():
        setattr(db_med, key, value)
    db.commit()
    db.refresh(db_med)

    return db_med

def delete_medication(db:Session, med_id: int, current_user: User):
    db_med = db.query(Medication).filter(Medication.id == med_id,
                                             Medication.user_id == current_user.id).first()
    if not db_med:
        return None
    db.delete(db_med)
    db.commit()
    return {"msg": "Medication deleted successfully"}

def update_medication_status(db:Session, med_id: int, status: MedicationStatus, current_user: User):
    db_med = db.query(Medication).filter(Medication.id == med_id,
                                             Medication.user_id == current_user.id).first()
    if not db_med:
        return None

    db_med.status = status
    db.commit()
    db.refresh(db_med)
    return db_med

def create_log(db: Session, log: LogCreate, current_user: User):
    db_med = get_medications_by_id(db, log.medication_id, current_user)
    if not db_med:
        return None

    # we have to check if log already exists
    existing_log = db.query(MedicationLog).filter(MedicationLog.medication_id == log.medication_id,
                                                  MedicationLog.user_id == current_user.id,
                                                  MedicationLog.date == date.today()
                                                  ).first()
    if existing_log:
        return None
    db_log = MedicationLog(**log.model_dump(),
                           user_id = current_user.id,
                           date = date.today())
    
    db.add(db_log)
    
    db.commit()
    db.refresh(db_log)

    update_streak(db, log.medication_id, current_user.id, log.status)
    return db_log


def get_today_logs(db: Session, current_user: User):
    db_log = db.query(MedicationLog).filter(
        MedicationLog.user_id == current_user.id,
        MedicationLog.date == date.today()
    ).all()
    
    return db_log or [] 
def get_medication_logs(db:Session, med_id: int, current_user: User):
    db_log  = db.query(MedicationLog).filter(MedicationLog.medication_id == med_id,
                                             MedicationLog.user_id == current_user.id).all()
    
    
    return db_log



def get_or_create_streak(db: Session, med_id: int, user_id: int) -> Streak:
    streak = db.query(Streak).filter(
        Streak.medication_id == med_id,
        Streak.user_id == user_id).first()
    if not streak:
        streak = Streak(medication_id=med_id, user_id=user_id)
        db.add(streak)
        db.commit()
        db.refresh(streak)
    return streak

def update_streak(db:Session, med_id: int, user_id, log_status: LogStatus):
    db_streak = get_or_create_streak(db, med_id, user_id)

    if log_status == LogStatus.taken:
        db_streak.total_taken += 1
        db_streak.current_streak += 1

        if db_streak.current_streak > db_streak.longest_streak:
            db_streak.longest_streak = db_streak.current_streak

    elif log_status == LogStatus.missed:
        db_streak.total_missed += 1
        db_streak.current_streak = 0 # the streak end and now resets

    elif log_status == LogStatus.skipped:
        db_streak.total_skipped += 1
        db_streak.current_streak = 0 # the streak end and now resets
    

    medication = db.query(Medication).filter(Medication.id == med_id).first()
    total_days = medication.duration_days

    db_streak.completion_percentage = round((db_streak.total_taken / total_days) * 100, 2)

    db_streak.updated_at = utcnow()
    db.commit()
    db.refresh(db_streak)
    return db_streak