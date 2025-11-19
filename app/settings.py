import os
from pydantic.v1 import BaseModel


class Config(BaseModel):
    SERIAL_PORT = os.getenv("SERIAL_PORT", "COM3")
    BAUDRATE = int(os.getenv("BAUDRATE", "115200"))
    POLL_SECONDS = int(os.getenv("POLL_SECONDS", "60"))
    CHANNEL_IDS = [...]

config = Config()