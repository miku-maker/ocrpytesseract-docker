from os import getenv
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ocrpytesseract"
    mode: str
    dbpath: str

    class Config:
        env_file = f"ocrpytesseract/envs/{getenv('MODE')}.env"
