from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://chuwibot:chuwibot_secret@localhost:5432/chuwibot_db"
    SECRET_KEY: str = "cambiar-en-produccion"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
