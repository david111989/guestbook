from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки сервиса. Значения берутся из переменных окружения или файла .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_version: str = "dev"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "guestbook"
    postgres_user: str = "guestbook"
    postgres_password: str = "change-me"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
