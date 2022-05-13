import random
from functools import lru_cache

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    DEBUG: bool
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str

    API_KEY: str
    CLEAN_API_ADDRESSES: list[str]
    DIRTY_API_ADDRESSES: list[str]
    BROKER_API_ADDRESSES: list[str]
    BONUS_API_ADDRESSES: list[str]

    API_DOWNTIME: int = random.randint(1, 10)

    @validator('CLEAN_API_ADDRESSES', each_item=True, pre=True)
    def clean_api_addresses_should_be_in_lower_case(cls, v: str):
        return v.lower()

    @validator('DIRTY_API_ADDRESSES', each_item=True, pre=True)
    def dirty_api_addresses_should_be_in_lower_case(cls, v: str):
        return v.lower()

    @validator('BROKER_API_ADDRESSES', each_item=True, pre=True)
    def broker_api_addresses_should_be_in_lower_case(cls, v: str):
        return v.lower()

    @validator('BONUS_API_ADDRESSES', each_item=True, pre=True)
    def bonus_api_addresses_should_be_in_lower_case(cls, v: str):
        return v.lower()

    @property
    def api_addresses(self):
        return [
            *self.CLEAN_API_ADDRESSES,
            *self.DIRTY_API_ADDRESSES,
            # *self.BONUS_API_ADDRESSES
        ]

    @property
    def database_url(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        # return f'mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    class Config:
        env_file = 'src/.env.prod'
        # env_file = 'src/.env.dev'


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
