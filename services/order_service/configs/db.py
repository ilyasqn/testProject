from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True,
        env_prefix='DB__',
        extra='ignore'
    )
    URL: str


db_settings = Settings()
