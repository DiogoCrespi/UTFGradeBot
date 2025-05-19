from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Configurações da API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Turing Bot API"
    
    # Configurações do CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Configurações do servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Configurações do banco de dados
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "turing_bot_test"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "1597"
    
    # Configurações do scraper
    UTFPR_URL: str = "https://gradenahora.com.br/utfpr/grade_na_hora.html"
    CURSO_CODIGO: str = "04219"
    SELENIUM_HEADLESS: str = "true"
    SELENIUM_TIMEOUT: str = "30"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 