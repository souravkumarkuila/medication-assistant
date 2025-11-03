from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..database import get_db
from ..auth import get_current_user
from .. import models, schemas

router = APIRouter(prefix='/adherence', tags=['adherence'])

@router.get('/stats', response_model=schemas.AdherenceStats)
def get_stats(period_days: int = 30, db: Session = Depends(get_db), user=Depends(get_current_user)):
    since = datetime.utcnow() - timedelta(days=period_days)
    q = db.query(models.DoseLog).join(models.Medication).filter(
        models.Medication.user_id == user.id,
        models.DoseLog.scheduled_at >= since,
    )
    scheduled = q.count()
    taken = q.filter(models.DoseLog.status == 'taken').count()
    missed = q.filter(models.DoseLog.status == 'missed').count()
    rate = (taken / scheduled * 100.0) if scheduled else 0.0
    return schemas.AdherenceStats(period_days=period_days, scheduled=scheduled, taken=taken, missed=missed, adherence_rate=round(rate, 2))
