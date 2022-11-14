import os

from pydantic import BaseSettings


class Config(BaseSettings):
    class Config:
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )

    secret_key: str = (
        "django-insecure-5-wh%*_hny_@&#b+7+snq*)tik)a-+q@#()^qlpgeco2f8q&*8"
    )
    debug: bool = True
    allowed_hosts: list = []

    database_name: str
    database_user: str
    database_password: str
    database_host: str
    database_port: int = 5432

    scraper_api_key: str


# Lazily initialize the config variable using module-level __getattr__
# so that we can import the Config class without triggering config load.
_config = None


def __getattr__(name):
    if name == "config":
        global _config
        if _config is None:
            _config = load_config()
        return _config
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def load_config():
    env_file = os.getenv("ENV_FILE", ".env")
    return Config(_env_file=env_file)
