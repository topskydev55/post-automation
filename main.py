import time
from libs.ftp import read_file
from libs.api import cancel_existing_postings, create_new_postings
from libs.config import settings
from libs.database import Base, engine
from libs.model import Transportexchangegroup
from sqlalchemy.orm import sessionmaker
import pandas as pd

Session = sessionmaker(bind=engine)
session = Session()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    
    while True:
        df = read_file(settings.FTP_PATH, settings.FTP_USERNAME, settings.FTP_PASSWORD, settings.FTP_FILENAME)
        if df is not None:
            existing_loads = session.query(Transportexchangegroup).all()
            existing_job_numbers = {load.Job_Number for load in existing_loads}
            print(existing_job_numbers)
            csv_job_numbers = set(df["Job_Number"])
            print(csv_job_numbers)
            new_job_numbers = csv_job_numbers - existing_job_numbers
            print(new_job_numbers)
            for _, row in df[df["Job_Number"].isin(new_job_numbers)].iterrows():
                status, id, payload = create_new_postings(row)
                if status:
                    row["orderId"] = id
                    for key, value in payload.items():
                        if key == "from":
                            row["_from"] = value
                        else:
                            row[key] = value
                    session.add(Transportexchangegroup(**row))
                    session.commit()
                
            deleted_job_numbers = existing_job_numbers - csv_job_numbers
            print(deleted_job_numbers)
            for job_number in deleted_job_numbers:
                id = session.query(Transportexchangegroup).filter(Transportexchangegroup.Job_Number == job_number).first().orderId
                print(id)
                status = cancel_existing_postings(id)
                print(status)
                if status:
                    session.query(Transportexchangegroup).filter(Transportexchangegroup.Job_Number == row["Job_Number"]).delete()
                    session.commit()
                    print(True)
                
        print(f"Waiting for {settings.WAIT_TIME} minutes before the next download...")
        time.sleep(60 * settings.WAIT_TIME)