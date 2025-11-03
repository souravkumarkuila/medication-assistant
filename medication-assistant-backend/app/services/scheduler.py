from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from dateutil import tz
import json

from ..database import SessionLocal
from .. import models

scheduler = BackgroundScheduler()


def _should_schedule_for_day(days_of_week: str, dt: date) -> bool:
    if days_of_week == 'all':
        return True
    days = {int(x) for x in days_of_week.split(',') if x != ''}
    return dt.weekday() in days


def generate_todays_schedules(db: Session):
    today = date.today()
    now = datetime.now(tz=tz.tzlocal()).replace(tzinfo=None)
    meds = db.query(models.Medication).all()
    for m in meds:
        if m.start_date and today < m.start_date:
            continue
        if m.end_date and today > m.end_date:
            continue
        if not _should_schedule_for_day(m.days_of_week, today):
            continue
        try:
            times = json.loads(m.times_of_day or '[]')
        except Exception:
            times = []
        for t in times:
            hour, minute = map(int, t.split(':'))
            scheduled_at = datetime(today.year, today.month, today.day, hour, minute)
            exists = db.query(models.DoseLog).filter(
                models.DoseLog.medication_id == m.id,
                models.DoseLog.scheduled_at == scheduled_at,
            ).first()
            if not exists:
                db.add(models.DoseLog(medication_id=m.id, scheduled_at=scheduled_at, status='scheduled'))
    db.commit()


def check_missed_doses(db: Session):
    now = datetime.utcnow()
    pending = db.query(models.DoseLog).filter(models.DoseLog.status == 'scheduled', models.DoseLog.scheduled_at < now - timedelta(minutes=60)).all()
    for d in pending:
        d.status = 'missed'
    if pending:
        db.commit()


def job_tick():
    db = SessionLocal()
    try:
        generate_todays_schedules(db)
        check_missed_doses(db)
    finally:
        db.close()


def start():
    scheduler.add_job(job_tick, 'interval', minutes=5, id='tick', replace_existing=True)
    scheduler.start()


def shutdown():
    scheduler.shutdown()
