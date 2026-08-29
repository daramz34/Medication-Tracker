from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from models import User
from schemas import ( MedicationStatusUpdate,
    MedicatedUpdate, MedicatedResponse,MedicationCreate
)
from crud import (
    delete_medication,
    create_medication,update_medication, update_medication_status, get_all_medications, get_medications_by_id
)
from sqlalchemy.orm import Session
from enums import MedicationStatus
from core.dependencies import get_current_user


router = APIRouter(prefix="/medications", tags=["MEDICATIONS"])


@router.post("/", response_model=MedicatedResponse, status_code=status.HTTP_201_CREATED, description="Create medication")
def create_med(med: MedicationCreate, db: Session = Depends(get_db),  current_user: User = Depends(get_current_user)):
    return create_medication(db, med, current_user)

@router.get("/", response_model=list[MedicatedResponse], status_code=status.HTTP_200_OK, description="Get meds")
def get_all_meds(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meds = get_all_medications(db, current_user)
    if not meds:
        raise HTTPException(status_code=404, detail="No medications found")
    return meds


@router.get("/{med_id}", response_model=MedicatedResponse, status_code=status.HTTP_200_OK, description="Get med by id")
def get_meds_by_id(med_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    med = get_medications_by_id(db, med_id, current_user)
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med

@router.patch("/{med_id}", response_model=MedicatedResponse, status_code=status.HTTP_200_OK, description="Update meds")
def update_meds(med_id: int, update: MedicatedUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_update = update_medication(db, med_id, update, current_user)
    if not db_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unable to update"
        )
    return db_update

@router.delete("/{med_id}",  status_code=status.HTTP_204_NO_CONTENT, description="Delete meds")
def delete_meds(med_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete = delete_medication(db, med_id, current_user)
    if not delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Med not found"
        )
    return 

@router.patch("/{med_id}/status", response_model=MedicatedResponse, status_code=status.HTTP_200_OK, description="Update med status")
def update_med_status(med_id: int, update:MedicationStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_update = update_medication_status(db, med_id, update.status, current_user)
    if not db_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Med not found"
        )
    return db_update


