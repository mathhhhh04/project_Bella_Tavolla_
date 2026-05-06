from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Bella Tavola API"
    app_version: str = "1.0.0"
    app_description: str = "API do restaurante Bella Tavola"
    debug: bool = False
    max_mesas: int = 20
    max_pessoas_por_mesa: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
