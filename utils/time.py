from datetime import datetime, timedelta


def pass_time(date: datetime, hours: int = 0, minutes: int = 0) -> datetime:
    return date + timedelta(hours=hours, minutes=minutes)


def save_format(date: datetime) -> str:
    return f"{date.year}_{date.month}_{date.day}_{date.hour}_{date.minute}_{date.second}"

def date_format(date:str) -> str:
    split_date = date.split("_")
    return f"{split_date[2]}/{split_date[1]}/{split_date[0]} - {split_date[3]}:{split_date[4]}:{split_date[5]}"

def datetime_format(date:str) -> datetime:
    split_date = date.split("_")
    return datetime(
        int(split_date[0]), 
        int(split_date[1]), 
        int(split_date[2]),
        int(split_date[3]),
        int(split_date[4]),
        int(split_date[5])
    )