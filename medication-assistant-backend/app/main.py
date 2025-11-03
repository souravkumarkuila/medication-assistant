import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .config import settings
from .routers import users, medications, adherence, chat, reminders
from .services.scheduler import start as start_scheduler, shutdown as stop_scheduler

# Create tables if they don't exist (for dev). In production, prefer Alembic migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Medication Assistant Backend",
    version="1.0.0",
)

# CORS configuration from environment (.env)
# Example: CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router)
app.include_router(medications.router)
app.include_router(adherence.router)
app.include_router(chat.router)
app.include_router(reminders.router)

# Background scheduler lifecycle
@app.on_event("startup")
async def _startup():
    start_scheduler()

@app.on_event("shutdown")
async def _shutdown():
    stop_scheduler()

# Health & root
@app.get("/health", tags=["system"])
async def health():
    return {"status": "healthy"}

@app.get("/", tags=["system"])
async def root():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)