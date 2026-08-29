from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from models import User
from schemas import ( 
    LogCreate, LogResponse
)
from crud import (
    create_log, get_today_logs, get_medication_logs, get_medications_by_id
)
from sqlalchemy.orm import Session
from enums import LogStatus
from core.dependencies import get_current_user



router = APIRouter(prefix="/logs", tags=["MEDICATIONS_LOGS"])


@router.post("/", response_model=LogResponse, status_code=status.HTTP_201_CREATED, description="Log medication intake")
def log_intake(log: LogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    result = create_log(db, log, current_user)
    
    if result is None:
        
        med = get_medications_by_id(db, log.medication_id, current_user)
        if not med:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already logged this medication today"
        )
    
    return result


@router.get("/today", response_model=list[LogResponse], status_code=200, description="Get today's logs")
def todays_logs(db:Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    return get_today_logs(db, current_user)

@router.get("/{med_id}", response_model=list[LogResponse], status_code=200, description="Get full log history")
def med_logs(med_id: int, db:Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    med = get_medications_by_id(db, med_id, current_user)
    if not med:
        raise HTTPException(
            status_code=404,
            detail="Medication not found"
        )
    logs = get_medication_logs(db, med_id, current_user)
    
    return logs