from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from models import User
from schemas import ( 
    StreakResponse
)
from crud import (
    get_or_create_streak)
from sqlalchemy.orm import Session
from core.dependencies import get_current_user



router = APIRouter(prefix="/streaks", tags=["MEDICATIONS_STREAKS"])


@router.get("/{med_id}", response_model=StreakResponse, status_code=status.HTTP_200_OK, description="Get Streak stats")
def streak(med_id: int, db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    db_streak = get_or_create_streak(db, med_id, current_user.id)
    
    return db_streak