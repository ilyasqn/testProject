from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True,
        env_prefix='JWT__',
        extra='ignore'
    )

    SECRET_KEY: str
    ALGORITHM: str


jwt_settings = Settings()
