from typing import final

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


@final
class DatabaseSettings(BaseSettings):
    """Database configuration.

    Reads the full SQLAlchemy URL from DATABASE_URL so the same code works
    across PostgreSQL, MySQL, and SQLite. Engine-specific fields are kept
    as optional fallbacks for code that references them directly.
    """

    database_url: str = Field("", alias="DATABASE_URL")

    # PostgreSQL fields (kept always for backwards-compat with Settings facade).
    postgres_user: str = Field("", alias="POSTGRES_USER")
    postgres_password: str = Field("", alias="POSTGRES_PASSWORD")
    postgres_server: str = Field("", alias="POSTGRES_SERVER")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    postgres_db: str = Field("", alias="POSTGRES_DB")

{% if cookiecutter.use_database == "mysql" %}
    mysql_user: str = Field("", alias="MYSQL_USER")
    mysql_password: str = Field("", alias="MYSQL_PASSWORD")
    mysql_server: str = Field("", alias="MYSQL_SERVER")
    mysql_port: int = Field(3306, alias="MYSQL_PORT")
    mysql_db: str = Field("", alias="MYSQL_DB")
{% endif %}

{% if cookiecutter.use_database == "sqlite" %}
    sqlite_db_path: str = Field("app.db", alias="SQLITE_DB_PATH")
    sqlite_db_dir: str = Field("./data", alias="SQLITE_DB_DIR")
{% endif %}

    @computed_field
    def sqlalchemy_database_uri(self) -> str:
        return self.database_url

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
