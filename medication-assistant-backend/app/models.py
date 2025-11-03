from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    medications = relationship('Medication', back_populates='owner', cascade='all, delete')

class Medication(Base):
    __tablename__ = 'medications'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, default=None)
    start_date: Mapped[datetime | None] = mapped_column(Date, default=None)
    end_date: Mapped[datetime | None] = mapped_column(Date, default=None)
    times_of_day: Mapped[str] = mapped_column(Text, default='[]')  # JSON list of 'HH:MM'
    days_of_week: Mapped[str] = mapped_column(String(32), default='all')  # 'all' or comma of 0-6

    owner = relationship('User', back_populates='medications')
    doses = relationship('DoseLog', back_populates='medication', cascade='all, delete')

class DoseLog(Base):
    __tablename__ = 'dose_logs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    medication_id: Mapped[int] = mapped_column(ForeignKey('medications.id', ondelete='CASCADE'))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    taken_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    status: Mapped[str] = mapped_column(String(32), default='scheduled')  # scheduled|taken|missed|skipped
    notes: Mapped[str | None] = mapped_column(Text, default=None)

    medication = relationship('Medication', back_populates='doses')
