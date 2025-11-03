from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..services.scheduler import generate_todays_schedules, check_missed_doses

router = APIRouter(prefix='/reminders', tags=['reminders'])

@router.post('/sync')
def sync(db: Session = Depends(get_db), user=Depends(get_current_user)):
    generate_todays_schedules(db)
    check_missed_doses(db)
    return {"status": "ok"}
