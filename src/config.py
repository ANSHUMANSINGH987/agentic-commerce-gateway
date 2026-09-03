from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str
    EMBEDDING_DIM: int = 1536

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()