from fastapi import APIRouter, Depends
from ..auth import get_current_user
from .. import schemas
from ..services.azure_openai import chat as ai_chat

router = APIRouter(prefix='/chat', tags=['chat'])

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a helpful healthcare medication assistant. "
        "You can explain medication schedules, adherence tips, and general information. "
        "Do NOT provide medical diagnosis. Always recommend consulting a professional for medical concerns."
    ),
}

@router.post('', response_model=schemas.ChatResponse)
async def chat(req: schemas.ChatRequest, user=Depends(get_current_user)):
    messages = [SYSTEM_PROMPT] + [m.model_dump() for m in req.messages]
    reply = await ai_chat(messages)
    return schemas.ChatResponse(reply=reply)
