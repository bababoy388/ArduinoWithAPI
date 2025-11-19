import os
from typing import List
from pydantic.v1 import BaseModel


class Config(BaseModel):
    SERIAL_PORT: str = os.getenv("SERIAL_PORT", "COM3")
    BAUDRATE: int = int(os.getenv("BAUDRATE", "115200"))
    POLL_SECONDS: int = int(os.getenv("POLL_SECONDS", "60"))
    CHANNEL_IDS: List[str] = ["UCqZvYprH2ornRwwMYbPoDYA"]

config = Config()