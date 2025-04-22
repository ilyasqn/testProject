from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:admin@localhost:5432/llm_webhook"

    class Config:
        env_file = ".env"


db_settings = Settings()