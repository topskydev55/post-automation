import time
import os
from dotenv import load_dotenv
from ftp import download_file
from csv_handler import CSVFileHandler

load_dotenv()

WAIT_TIME: int = int(os.getenv("WAIT_TIME"))
API_URL: str = os.getenv("API_URL")
API_TOKEN: str = os.getenv("API_TOKEN")
FTP_PATH: str = os.getenv("FTP_PATH")
FTP_USERNAME: str = os.getenv("FTP_USERNAME")
FTP_PASSWORD: str = os.getenv("FTP_PASSWORD")
FTP_FILENAME: str = os.getenv("FTP_FILENAME")

if __name__ == "__main__":
    file_handler = CSVFileHandler(API_URL, API_TOKEN)
    while True:
        result = download_file(FTP_PATH, FTP_USERNAME, FTP_PASSWORD, FTP_FILENAME)
        if result == True:
            file_handler.handle_file_change(FTP_FILENAME)
        print(f"Waiting for {WAIT_TIME} minutes before the next download...")
        time.sleep(60 * WAIT_TIME)