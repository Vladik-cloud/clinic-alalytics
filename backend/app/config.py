from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://cliniciq_readonly:cliniciq_readonly@localhost:5432/cliniciq"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"


settings = Settings()
