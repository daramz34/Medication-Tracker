from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from datetime import datetime, date as date_type, time
from enums import LogStatus, MedicationStatus, Frequency


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class MedicationCreate(BaseModel):
    name: str
    description: str
    dosage: str
    frequency: Frequency
    duration_days: int
    start_date: date_type
    reminder_time: time
    reminder_enabled: bool = True
    

class MedicatedResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: str
    dosage: str
    frequency: Frequency
    duration_days: int
    start_date: date_type
    end_date: date_type
    status: MedicationStatus
    reminder_time: time
    reminder_enabled: bool
    created_at: datetime

    model_config= ConfigDict(from_attributes=True)


class MedicatedUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[Frequency]= None
    duration_days: Optional[int] = None
    start_date: Optional[date_type]= None
    reminder_time: Optional[time] = None
    reminder_enabled: Optional[bool] = None
    status: Optional[MedicationStatus] = None

class MedicationStatusUpdate(BaseModel):
    status: MedicationStatus

class LogCreate(BaseModel):
    medication_id: int
    status: LogStatus
    notes: Optional[str] = Field(None, max_length=150)

class LogResponse(BaseModel):
    id: int
    medication_id: int
    date: date_type
    status: LogStatus
    taken_at: Optional[time] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config= ConfigDict(from_attributes=True)

class StreakResponse(BaseModel):
    medication_id: int
    current_streak: int
    longest_streak: int
    total_taken: int
    total_missed: int
    total_skipped: int
    completion_percentage: float

    model_config= ConfigDict(from_attributes=True)


