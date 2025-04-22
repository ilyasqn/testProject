from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openrouter_api_key: str = "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"
    openrouter_model: str = "gpt-3.5-turbo"

    class Config:
        env_file = ".env"


settings = Settings()
