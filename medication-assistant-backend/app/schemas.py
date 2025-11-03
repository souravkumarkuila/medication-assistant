# from pydantic import BaseModel, EmailStr, field_validator
# from typing import List, Optional
# from datetime import datetime, date

# # Auth
# class UserCreate(BaseModel):
#     email: EmailStr
#     password: str
#     full_name: Optional[str] = None

# class UserOut(BaseModel):
#     id: int
#     email: EmailStr
#     full_name: Optional[str] = None
#     class Config:
#         from_attributes = True

# class Token(BaseModel):
#     access_token: str
#     token_type: str = 'bearer'

# # Medication
# class MedicationBase(BaseModel):
#     name: str
#     dosage: str
#     notes: Optional[str] = None
#     start_date: Optional[date] = None
#     end_date: Optional[date] = None
#     times_of_day: List[str] = []
#     days_of_week: str = 'all'

#     @field_validator('times_of_day')
#     @classmethod
#     def validate_times(cls, v):
#         for t in v:
#             if len(t) != 5 or t[2] != ':':
#                 raise ValueError('time format must be HH:MM')
#         return v

# class MedicationCreate(MedicationBase):
#     pass

# class MedicationUpdate(MedicationBase):
#     pass

# class MedicationOut(MedicationBase):
#     id: int
#     class Config:
#         from_attributes = True

# class DoseLogOut(BaseModel):
#     id: int
#     scheduled_at: datetime
#     taken_at: Optional[datetime] = None
#     status: str
#     notes: Optional[str] = None
#     class Config:
#         from_attributes = True

# # Chat
# class ChatMessage(BaseModel):
#     role: str
#     content: str

# class ChatRequest(BaseModel):
#     messages: List[ChatMessage]

# class ChatResponse(BaseModel):
#     reply: str

# # Adherence
# class AdherenceStats(BaseModel):
#     period_days: int
#     scheduled: int
#     taken: int
#     missed: int
#     adherence_rate: float

from pydantic import BaseModel, EmailStr, field_validator, constr
from typing import List, Optional
from datetime import datetime, date

# =========================
# Auth Schemas
# =========================
class UserCreate(BaseModel):
    email: EmailStr
    # Enforce sensible bounds; bcrypt_sha256 supports long passwords, but we still guard extremes
    password: constr(min_length=8, max_length=128)
    full_name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# =========================
# Medication Schemas
# =========================
class MedicationBase(BaseModel):
    name: str
    dosage: str
    notes: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    times_of_day: List[str] = []
    # 'all' or comma-separated 0-6 (Mon-Sun). We keep string to keep backend logic simple.
    days_of_week: str = "all"

    @field_validator("times_of_day")
    @classmethod
    def validate_times(cls, v: List[str]) -> List[str]:
        """
        Validates 'HH:MM' 24-hour format.
        Example: '08:00', '20:30'
        """
        for t in v:
            if len(t) != 5 or t[2] != ":":
                raise ValueError("time format must be HH:MM")
            hh, mm = t.split(":")
            if not (hh.isdigit() and mm.isdigit()):
                raise ValueError("time must be numeric in HH:MM")
            h, m = int(hh), int(mm)
            if h < 0 or h > 23 or m < 0 or m > 59:
                raise ValueError("time must be a valid 24-hour time (00:00 to 23:59)")
        return v


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(MedicationBase):
    pass


class MedicationOut(MedicationBase):
    id: int

    class Config:
        from_attributes = True


# =========================
# Dose Logs
# =========================
class DoseLogOut(BaseModel):
    id: int
    scheduled_at: datetime
    taken_at: Optional[datetime] = None
    status: str  # scheduled|taken|missed|skipped
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# Chat Schemas
# =========================
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    reply: str


# =========================
# Adherence Schemas
# =========================
class AdherenceStats(BaseModel):
    period_days: int
    scheduled: int
    taken: int
    missed: int
    adherence_rate: float