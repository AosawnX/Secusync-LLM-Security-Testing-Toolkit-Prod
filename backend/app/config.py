from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SECUSYNC API"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./secusync.db"

    # We will add other keys here later (e.g. OPENAI_API_KEY, ANTHROPIC_API_KEY)
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
