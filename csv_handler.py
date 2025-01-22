import os
import pandas as pd
import requests
from utils import get_datetime_range


class CSVFileHandler():
    def __init__(self, API_URL, API_TOKEN):
        self.API_URL = API_URL
        self.API_TOKEN = API_TOKEN
        
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-API-KEY": API_TOKEN
        }
        self.payload = {
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
        
        self.prev_data = None
        self.prev_modified_time = None
        
    
    def handle_file_change(self, file_path):
        if os.path.getmtime(file_path) != self.prev_modified_time:
            print(f"{file_path} has been modified at {os.path.getmtime(file_path)}.")
            new_data = self.read_csv(file_path)
            if self.prev_data is not None:
                self.cancel_existing_postings()
            self.prev_data = self.create_new_postings(new_data)
            self.prev_modified_time = os.path.getmtime(file_path)

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
                response = requests.delete(f"{self.API_URL}/load/{posting_id}", headers=self.headers)
                if response.status_code == 200:
                    print(f"{posting_id} removed successfully.")
                else:
                    print(f"Failed to remove {posting_id}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error removing existing postings: {e}")

    def create_new_postings(self, data):
        ids = []
        for _, row in data.iterrows():
            try:
                self.payload["customerReference"] = row["Job_Number"]
                self.payload["commodity"] = row["Goods"]
                self.payload["grossWeight"] = {
                    "units": "kg",
                    "value": row["Weight"]
                }
                self.payload["from"]["town"] = row["Collection_Add_4"]
                self.payload["from"]["postcode"] = row["Collection_PostCode"]
                self.payload["readyAt"], self.payload["collectBy"] = get_datetime_range(row["Collection_Date"], row["Collection_Time"])
                self.payload["to"]["town"] = row["Delivery_Add_4"]
                self.payload["to"]["postcode"] = row["Delivery_PostCode"]
                self.payload["deliverFrom"], self.payload["deliverBy"] = get_datetime_range(row["Delivery_Date"], row["Delivery_Time"])
                if(self.payload["deliverFrom"] < self.payload["readyAt"]):
                    readyAt_time = self.datetime.strptime(self.payload["readyAt"], '%Y-%m-%dT%H:%M:%SZ')
                    new_deliverFrom = readyAt_time + self.timedelta(hours=1)
                    self.payload["deliverFrom"] = new_deliverFrom.strftime('%Y-%m-%dT%H:%M:%SZ')
                
                response = requests.post(f"{self.API_URL}/loads", json=self.payload, headers=self.headers)
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