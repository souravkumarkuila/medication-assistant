from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime, date, timedelta

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix='/medications', tags=['medications'])

@router.post('', response_model=schemas.MedicationOut)
def create_med(payload: schemas.MedicationCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    med = models.Medication(
        user_id=user.id,
        name=payload.name,
        dosage=payload.dosage,
        notes=payload.notes,
        start_date=payload.start_date,
        end_date=payload.end_date,
        times_of_day=json.dumps(payload.times_of_day),
        days_of_week=payload.days_of_week,
    )
    db.add(med)
    db.commit()
    db.refresh(med)
    return med

@router.get('', response_model=List[schemas.MedicationOut])
def list_meds(db: Session = Depends(get_db), user=Depends(get_current_user)):
    meds = db.query(models.Medication).filter(models.Medication.user_id == user.id).all()
    return meds

@router.get('/{med_id}', response_model=schemas.MedicationOut)
def get_med(med_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id, models.Medication.user_id == user.id).first()
    if not med:
        raise HTTPException(404, 'Not found')
    return med

@router.put('/{med_id}', response_model=schemas.MedicationOut)
def update_med(med_id: int, payload: schemas.MedicationUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id, models.Medication.user_id == user.id).first()
    if not med:
        raise HTTPException(404, 'Not found')
    med.name = payload.name
    med.dosage = payload.dosage
    med.notes = payload.notes
    med.start_date = payload.start_date
    med.end_date = payload.end_date
    med.times_of_day = json.dumps(payload.times_of_day)
    med.days_of_week = payload.days_of_week
    db.commit()
    db.refresh(med)
    return med

@router.delete('/{med_id}')
def delete_med(med_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id, models.Medication.user_id == user.id).first()
    if not med:
        raise HTTPException(404, 'Not found')
    db.delete(med)
    db.commit()
    return {"status": "deleted"}

@router.post('/{med_id}/doses/{dose_id}/take')
def take_dose(med_id: int, dose_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    dose = db.query(models.DoseLog).join(models.Medication).filter(
        models.DoseLog.id == dose_id,
        models.Medication.user_id == user.id,
        models.Medication.id == med_id,
    ).first()
    if not dose:
        raise HTTPException(404, 'Dose not found')
    dose.status = 'taken'
    dose.taken_at = datetime.utcnow()
    db.commit()
    return {"status": "taken"}

@router.get('/{med_id}/doses', response_model=List[schemas.DoseLogOut])
def list_doses(med_id: int, days: int = 7, db: Session = Depends(get_db), user=Depends(get_current_user)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id, models.Medication.user_id == user.id).first()
    if not med:
        raise HTTPException(404, 'Not found')
    since = datetime.utcnow() - timedelta(days=days)
    doses = db.query(models.DoseLog).filter(models.DoseLog.medication_id == med.id, models.DoseLog.scheduled_at >= since).order_by(models.DoseLog.scheduled_at.asc()).all()
    return doses
