from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "PROD"
    test_user_email : str = ""
    test_user_password : str = ""
    secret_key : str = Field(..., env="SECRET_KEY")
    resend_api_key : str = Field(..., env="RESEND_API_KEY")

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()