# from pydantic_settings import BaseSettings
# from pydantic import Field

# class Settings(BaseSettings):
#     database_url: str = Field(alias='DATABASE_URL')
#     jwt_secret: str = Field(alias='JWT_SECRET', default='changeme')
#     jwt_algorithm: str = Field(alias='JWT_ALGORITHM', default='HS256')
#     access_token_expire_minutes: int = Field(alias='ACCESS_TOKEN_EXPIRE_MINUTES', default=60)

#     azure_openai_endpoint: str = Field(alias='AZURE_OPENAI_ENDPOINT', default='')
#     azure_openai_api_key: str = Field(alias='AZURE_OPENAI_API_KEY', default='')
#     azure_openai_deployment: str = Field(alias='AZURE_OPENAI_DEPLOYMENT', default='gpt-4o')
#     azure_openai_api_version: str = Field(alias='AZURE_OPENAI_API_VERSION', default='2025-01-01-preview')

#     class Config:
#         env_file = '.env'
#         case_sensitive = False

# settings = Settings()

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import json

class Settings(BaseSettings):
    # Database & Auth
    database_url: str = Field(alias='DATABASE_URL')
    jwt_secret: str = Field(alias='JWT_SECRET', default='changeme')
    jwt_algorithm: str = Field(alias='JWT_ALGORITHM', default='HS256')
    access_token_expire_minutes: int = Field(alias='ACCESS_TOKEN_EXPIRE_MINUTES', default=60)

    # Azure OpenAI
    azure_openai_endpoint: str = Field(alias='AZURE_OPENAI_ENDPOINT', default='')
    azure_openai_api_key: str = Field(alias='AZURE_OPENAI_API_KEY', default='')
    azure_openai_deployment: str = Field(alias='AZURE_OPENAI_DEPLOYMENT', default='gpt-4o')
    azure_openai_api_version: str = Field(alias='AZURE_OPENAI_API_VERSION', default='2025-01-01-preview')

    # CORS: accept JSON array or comma-separated in .env
    cors_allow_origins: List[str] = Field(
        alias='CORS_ALLOW_ORIGINS',
        default=['*']  # dev-friendly default; set explicit origins in prod
    )

    # pydantic-settings v2 config
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=False,
    )

    @field_validator('cors_allow_origins', mode='before')
    @classmethod
    def parse_cors(cls, v):
        """
        Accept:
          - JSON array: '["http://localhost:5173","http://localhost:3000"]'
          - CSV:        'http://localhost:5173,http://localhost:3000'
        """
        if v is None or v == '':
            return ['*']
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            # Try JSON first
            if s.startswith('['):
                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    # fall through to CSV parsing if JSON fails
                    pass
            # CSV fallback
            return [x.strip() for x in s.split(',') if x.strip()]
        return v

settings = Settings()
