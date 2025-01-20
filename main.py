import time
import pandas as pd
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

API_URL: str = os.getenv("API_URL")
API_TOKEN: str = os.getenv("API_TOKEN")

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-API-KEY": API_TOKEN
}

payload = {
    "freightType": "NA",
    "jobDescription": "DELIVER_DIRECT",
    "minVehicleSize": "13.6M",
    "phoneNumber":  "+441482326471",
    "quotesEnabled": True,
    "podHardCopiesRequired": True,
    "bodyType": "CURTAIN",
    "from": {
        "country": "GB"
    },
    "to": {
        "country": "GB"
    }
}

def get_datetime_range(date_str, time_range):
    try:
        collection_date = datetime.strptime(date_str, '%d/%m/%Y')

        start_time_str, end_time_str = time_range.split('-')
        start_time = datetime.strptime(start_time_str, '%H:%M')
        end_time = datetime.strptime(end_time_str, '%H:%M')

        start_datetime = datetime(collection_date.year, collection_date.month, collection_date.day, start_time.hour, start_time.minute)
        end_datetime = datetime(collection_date.year, collection_date.month, collection_date.day, end_time.hour, end_time.minute)

        start_iso = start_datetime.isoformat() + 'Z'
        end_iso = end_datetime.isoformat() + 'Z'

        return start_iso, end_iso
    except:
        print("Error parsing date/time. Please ensure the format is correct.")
        return None, None


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.prev_data = None
        self.prev_modified_time = None
    
    def on_modified(self, event):
        if event.src_path.endswith('.csv') and os.path.getmtime(event.src_path) != self.prev_modified_time:
            print(f"{event.src_path} has been modified at {os.path.getmtime(event.src_path)}.")
            new_data = self.read_csv(event.src_path)
            if self.prev_data is not None:
                self.cancel_existing_postings()
            self.prev_data = self.create_new_postings(new_data)
            self.prev_modified_time = os.path.getmtime(event.src_path)

    def read_csv(self, file_path):
        try:
            data = pd.read_csv(file_path)
            return data
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None

    def cancel_existing_postings(self):
        print('cancel_existing_postings', self.prev_data)
        try:
            for posting_id in self.prev_data:
                response = requests.delete(f"{API_URL}/load/{posting_id}", headers=headers)
                if response.status_code == 200:
                    print(f"{posting_id} removed successfully.")
                else:
                    print(f"Failed to remove {posting_id}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error removing existing postings: {e}")

    def create_new_postings(self, data):
        ids = []
        for _, row in data.iterrows():
            payload["customerReference"] = row["Job_Number"]
            payload["commodity"] = row["Goods"]
            payload["grossWeight"] = {
                "units": "kg",
                "value": row["Weight"]
            }
            payload["from"]["town"] = row["Collection_Add_4"]
            payload["from"]["postcode"] = row["Collection_PostCode"]
            payload["readyAt"], payload["collectBy"] = get_datetime_range(row["Collection_Date"], row["Collection_Time"])
            payload["to"]["town"] = row["Delivery_Add_4"]
            payload["to"]["postcode"] = row["Delivery_PostCode"]
            payload["deliverFrom"], payload["deliverBy"] = get_datetime_range(row["Delivery_Date"], row["Delivery_Time"])
            if(payload["deliverFrom"] < payload["readyAt"]):
                readyAt_time = datetime.strptime(payload["readyAt"], '%Y-%m-%dT%H:%M:%SZ')
                new_deliverFrom = readyAt_time + timedelta(hours=1)
                payload["deliverFrom"] = new_deliverFrom.strftime('%Y-%m-%dT%H:%M:%SZ')
            try:
                response = requests.post(f"{API_URL}/loads", json=payload, headers=headers)
                data = response.json()
                if response.status_code < 400:
                    print(f"Successfully created posting for {data.get('id')}.")
                    ids.append(data.get('id'))
                else:
                    print(f"Failed. Status code: {response.status_code}, Response: {response.json()}")
                    print(f"Job_Number: {row['Job_Number']}")
            except Exception as e:
                print(f"Error creating posting: {e}")
        return ids

def monitor_file(file_path):
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=file_path, recursive=False)
    observer.start()
    print(f"Monitoring {file_path} for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    file_to_monitor = "."
    monitor_file(file_to_monitor)