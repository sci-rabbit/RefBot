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

    limit: int = 7
    period: int = 10

class SearchConfig(BaseModel):
    page_size: int = 30

class DatabaseConfig(BaseModel):
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    user: str
    password: str
    host: str
    port: int
    name: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    bot: BotConfig
    tg_client: TgClientConfig
    redis: RedisConfig
    db: DatabaseConfig
    search: SearchConfig = SearchConfig()

settings = Settings()
