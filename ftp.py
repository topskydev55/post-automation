from ftplib import FTP

def download_file(ftp_path, username, password, filename):
    try:
        ftp = FTP(ftp_path)
        ftp.login(user=username, passwd=password)

        ftp.cwd('.')
        ftp.retrlines('LIST')

        with open(filename, 'wb') as file:
            ftp.retrbinary(f'RETR {filename}', file.write)

        print(f"File '{filename}' downloaded successfully.")
        
        ftp.quit()
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False