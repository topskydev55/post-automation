from ftplib import FTP
import io
import pandas as pd

def read_file(ftp_path, username, password, filename):
    try:
        ftp = FTP(ftp_path)
        ftp.login(user=username, passwd=password)
        file_buffer = io.BytesIO()
        ftp.retrbinary(f'RETR {filename}', file_buffer.write)
        
        file_buffer.seek(0)
        
        df = pd.read_csv(io.TextIOWrapper(file_buffer, encoding='utf-8', errors='ignore'))
        
        print(f"File '{filename}' read successfully.")
        
        ftp.quit()
        return df
    except Exception as e:
        print(f"An error occurred: {e}")
        return None