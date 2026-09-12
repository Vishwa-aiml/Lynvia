from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/lynvia"
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    # Allow a comma-separated list or a single origin; default is '*' (allow all)
    BACKEND_CORS_ORIGINS: Optional[str] = "*"
    
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    PLATFORM_COMMISSION_RATE: float = 0.12
    # Withdrawal settings
    MINIMUM_WITHDRAWAL_AMOUNT: int = 10000  # ₹100 in paise (minor units)
    WITHDRAWAL_CURRENCY: str = "INR"
    # Admin authorization — authorized admin email (case-insensitive comparison)
    ADMIN_EMAIL: str = "vspark2908@gmail.com"
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
