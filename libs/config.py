import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_NAME=os.getenv("DB_NAME")
    DB_USER=os.getenv("DB_USER")
    DB_PASSWORD=os.getenv("DB_PASSWORD")
    DB_HOST=os.getenv("DB_HOST")
    DB_PORT=os.getenv("DB_PORT")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
    WAIT_TIME: int = int(os.getenv("WAIT_TIME"))
    API_URL: str = os.getenv("API_URL")
    API_TOKEN: str = os.getenv("API_TOKEN")
    FTP_PATH: str = os.getenv("FTP_PATH")
    FTP_USERNAME: str = os.getenv("FTP_USERNAME")
    FTP_PASSWORD: str = os.getenv("FTP_PASSWORD")
    FTP_FILENAME: str = os.getenv("FTP_FILENAME")
    
settings = Settings()