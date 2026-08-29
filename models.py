from sqlalchemy import Column, String, Integer, Float,Date,Time,Text, Boolean,  Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone, date, time
from enums import Frequency, LogStatus,MedicationStatus
def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    medication = relationship("Medication", back_populates="user", cascade="all, delete")
    log = relationship("MedicationLog", back_populates="user", cascade="all, delete")
    streak = relationship("Streak", back_populates="user", cascade="all, delete")



class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # foreignkey
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(Enum(Frequency), default=Frequency.three_times_daily, nullable=False)
    duration_days = Column(Integer, nullable=False)
    start_date = Column(Date, default=date.today, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(Enum(MedicationStatus), default=MedicationStatus.active, nullable=False)
    reminder_time = Column(Time, nullable=False)
    reminder_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)


    user = relationship("User", back_populates="medication")
    log = relationship("MedicationLog", back_populates="medication", cascade="all, delete-orphan")
    streak = relationship("Streak", back_populates="medication", cascade="all, delete-orphan")


class MedicationLog(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    medication_id = Column(Integer, ForeignKey("medications.id", ondelete="CASCADE"), nullable=False)  # foreignkey
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # foreignkey
    date = Column(Date, default=date.today, nullable=False)
    status = Column(Enum(LogStatus), nullable=False)
    taken_at = Column(Time, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="log")
    medication = relationship("Medication", back_populates="log")


class Streak(Base):
    __tablename__ = "streaks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    medication_id = Column(Integer, ForeignKey("medications.id", ondelete="CASCADE"), nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_taken = Column(Integer, default=0)
    total_missed = Column(Integer, default=0)
    total_skipped = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    user = relationship("User", back_populates="streak")
    medication = relationship("Medication", back_populates="streak")

