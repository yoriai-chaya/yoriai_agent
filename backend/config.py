import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_max_turns: int = 3
    log_dir: str = "log"
    output_dir: Path = Path("output")
    test_results_dir: Path = Path("results")
    playwright_customconfig_file: str = "playwright.customconfig.json"
    debug: bool = False
    code_gen_retry: int = 3

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env")
    )


@lru_cache
def get_settings():
    return Settings()
