import os
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


def load_docker_secrets():
    for key, value in list(os.environ.items()):
        if key.endswith("_FILE"):
            target_key = key[:-5]
            file_path = Path(value)
            if file_path.exists():
                os.environ[target_key] = file_path.read_text(encoding="utf-8").strip()


load_docker_secrets()


class BotConfig(BaseModel):
    token: str
    source_chat: int
    admin_ids: list


class TgClientConfig(BaseModel):
    api_id: int
    api_hash: str
    session: str


class RedisConfig(BaseModel):
    host: str
    password: str
    port: str
    ONE_WEEK: int = 60 * 60 * 24 * 7


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    bot: BotConfig
    tg_client: TgClientConfig
    redis: RedisConfig

    limit: int = 5000
    
    
settings = Settings()
