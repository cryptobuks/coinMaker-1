import datetime

def timestamp_from_date(date_time):
    date_time_obj = datetime.datetime.strptime(date_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    return date_time_obj.timestamp()