import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / '.env')

class Settings:
    PROJECT_NAME: str = "ResearchGuard"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    
    # Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/researchguard.db")
    
    # External Scholarly API Settings
    OPENALEX_EMAIL: str = os.getenv("OPENALEX_EMAIL", "")
    CROSSREF_MAILTO: str = os.getenv("CROSSREF_MAILTO", "")
    SEMANTIC_SCHOLAR_API_KEY: str = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    
    # Request timeouts (seconds)
    API_TIMEOUT: float = 12.0
    MAX_SCHOLARLY_CANDIDATES: int = 5
    CONCURRENCY_LIMIT: int = 5
    VERIFIED_SCORE: float = float(os.getenv('VERIFIED_SCORE', '82'))
    METADATA_MATCH_SCORE: float = float(os.getenv('METADATA_MATCH_SCORE', '70'))
    POSSIBLE_MATCH_SCORE: float = float(os.getenv('POSSIBLE_MATCH_SCORE', '45'))
    
    # File upload limits
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: set = {".pdf"}
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

settings = Settings()

# Ensure required directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
