from sqlalchemy import create_engine

from config import Config, config

config: Config
DATABASE_URL = config.database_url
engine = create_engine(DATABASE_URL)
