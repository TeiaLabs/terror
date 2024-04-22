from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TERROR_MONGODB_URI: str
    TERROR_MONGODB_DBNAME: str
