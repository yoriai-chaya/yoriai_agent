from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
import os


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str

    #model_config = SettingsConfigDict(env_file=".env")
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env")
    )

