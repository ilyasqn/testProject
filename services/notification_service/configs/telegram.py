from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True,
        env_prefix='TELEGRAM__',
        extra='ignore'
    )

    BOT_TOKEN: str
    CHAT_ID: str


telegram_settings = Settings()
