from pydantic import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str  # 'mysql+mysqlconnector://user:password@localhost/fastapi'
    # JWT configs
    SECRET_KEY: str  # '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
    ALGORITHM: str  # 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: float = 30

    class Config:
        env_file = '.env'


env = Settings()
