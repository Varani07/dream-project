from datetime import datetime, timedelta


def passar_tempo(data:datetime, horas:int=0, minutos:int=0):
    nova_data = data + timedelta(hours=horas, minutes=minutos)
    return nova_data

def formato_save(data:datetime) -> str:
    return f"{data.year}_{data.month}_{data.day}_{data.hour}_{data.minute}_{data.second}"
