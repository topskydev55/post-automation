from datetime import datetime

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
    except Exception as e:
        print(e)
        return None, None
