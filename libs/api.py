import requests
from libs.utils import get_datetime_range
from datetime import datetime, timedelta
from libs.config import settings

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-API-KEY": settings.API_TOKEN
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

def cancel_existing_postings(order_id):
    print('cancel_existing_posting: ', order_id)
    try:
        response = requests.delete(f"{settings.API_URL}/load/{order_id}", headers=headers)
        if response.status_code == 200:
            print(f"{order_id} removed successfully.")
            return True
        else:
            print(f"Failed to remove {order_id}. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error removing existing postings: {e}")
        return False

def create_new_postings(row):
    try:
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
        response = requests.post(f"{settings.API_URL}/loads", json=payload, headers=headers)
        data = response.json()
        if response.status_code < 400:
            print(f"Successfully created posting for {data.get('id')}.")
            return True, data.get('id'), payload
        else:
            print(f"Failed. Status code: {response.status_code}, Response: {response.json()}")
            print(f"Job_Number: {row['Job_Number']}")
            return False, None, None
    except Exception as e:
        print(f"Error creating posting: {e}")
        return False, None, None
