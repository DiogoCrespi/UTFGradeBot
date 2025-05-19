from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # Configurações da API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Turing Bot API"
    
    # Configurações do CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Configurações do servidor
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Configurações do banco de dados
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    
    # Configurações do scraper
    UTFPR_URL: str
    CURSOS_MEDIANEIRA: str  # Lê como string, faça o split depois se quiser lista
    SELENIUM_HEADLESS: bool
    SELENIUM_TIMEOUT: int

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()