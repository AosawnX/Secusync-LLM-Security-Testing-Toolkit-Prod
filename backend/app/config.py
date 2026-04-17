from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SECUSYNC API"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./secusync.db"

    HF_API_TOKEN: str | None = None
    HF_PARAPHRASE_ENDPOINT: str = "https://api-inference.huggingface.co/models/tuner007/pegasus_paraphrase"
    HF_TRANSLATE_EN_FR_ENDPOINT: str = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-fr"
    HF_TRANSLATE_FR_EN_ENDPOINT: str = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-fr-en"
    MUTATION_DEDUP_THRESHOLD: float = 0.95
    MUTATION_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    MAX_VARIANTS_PER_RUN: int = 50   # hard cap on total prompts per scan
    SCAN_REQUEST_DELAY_MS: int = 500 # rate-limit delay between TLLM calls

    # Auth — path to Firebase service account JSON (NEVER commit this file)
    FIREBASE_SERVICE_ACCOUNT_PATH: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
