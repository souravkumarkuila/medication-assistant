from openai import AzureOpenAI
from ..config import settings

_client = None

def get_client() -> AzureOpenAI:
    global _client
    if _client is None:
        _client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )
    return _client

async def chat(messages: list[dict]) -> str:
    client = get_client()
    try:
        resp = client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=messages,
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        return f"AI error: {e}"
