from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "PROD"
    test_user_email : str = ""
    test_user_password : str = ""

    model_config = SettingsConfigDict(env_file=".env")