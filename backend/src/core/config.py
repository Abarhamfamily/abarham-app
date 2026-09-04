from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Abarham App"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "sqlite:///./abarham.db"

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    STORAGE_TYPE: str = "local"
    UPLOAD_DIR: str = "./uploads"

    SMS_PROVIDER: str = "mock"

    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
