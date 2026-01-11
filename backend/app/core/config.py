import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class config(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")


config = config()
