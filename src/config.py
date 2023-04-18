from pydantic import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: float = 30

    class Config:
        env_file = '.env'


env = Settings()
