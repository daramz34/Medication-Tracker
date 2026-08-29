from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL:str
    SECRET_KEY:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    ALGORITHM:str

    APP_NAME: str = "MEDICATION_TRACKER"
    VERSION: str = "1.0.0"


    #mail
    SENDER_EMAIL:str
    GMAIL_PASSWORD:str

    BREVO_API_KEY: str = ""


    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parent.parent / ".env")


settings = Settings()

