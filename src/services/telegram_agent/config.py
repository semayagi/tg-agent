from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")

    llm_api_key: str = Field(alias="LLM_API_KEY")
    llm_model: str = Field(default="openai/gpt-oss-20b:free", alias="LLM_MODEL")
    llm_base_url: str = Field(default="https://openrouter.ai/api/v1/", alias="LLM_BASE_URL")

    giphy_api_key: str = Field(alias="GIPHY_API_KEY")
