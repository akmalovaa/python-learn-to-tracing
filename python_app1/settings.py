
from pydantic_settings import BaseSettings
from sqlalchemy.engine.url import URL


class Settings(BaseSettings):
    debug: bool = True

    db_driver: str = "postgresql+asyncpg"
    postgres_user: str = "opg_user"
    postgres_password: str = "opg_password"
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_database: str = "opg_db"

    database_dsn: str = (
        f"{db_driver}://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_database}"
    )
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_pre_ping: bool = True
    database_max_reties_count: int = 5

    redis_host: str = "redis"
    redis_port: int = 6379

    second_app_host: str = "app2"

    @property
    def db_dsn(self) -> URL:
        return URL.create(
            self.db_driver,
            self.postgres_user,
            self.postgres_password,
            self.postgres_host,
            self.postgres_port,
            self.postgres_database,
        )


settings = Settings()