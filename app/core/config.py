from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Meta
    PROJECT_NAME: str = "Taller - API Enterprise"
    API_V1_STR: str = "/api/v1"
    
    # Seguridad (JWT)
    SECRET_KEY: str = "CAMBIAR_ESTO_EN_PRODUCCION_O_ME_DESPIDEN_123!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 Días para comodidad de los alumnos
    
    # Base de Datos
    DATABASE_URL: str = "sqlite:///./fastapi.db"
    
    # Inteligencia Artificial
    GEMINI_API_KEY: str | None = None
    ZHIPU_API_KEY: str | None = None
    
    # Esta línea mágica le dice a Pydantic que lea automáticamente el archivo .env si existe
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

# Instanciamos la clase para importar `settings` en cualquier parte de la app
settings = Settings()
