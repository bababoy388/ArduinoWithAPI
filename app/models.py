from pydantic_settings import BaseSettings


class AddChannelBody(BaseSettings):
    channel_id: str