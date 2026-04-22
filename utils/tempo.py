from datetime import datetime, timedelta


def passar_tempo(data:datetime, horas:int=0, minutos:int=0):
    nova_data = data + timedelta(hours=horas, minutes=minutos)
    return nova_data

def formato_save(data:datetime) -> str:
    return f"{data.year}_{data.month}_{data.day}_{data.hour}_{data.minute}_{data.second}"

def formato_data(data:str) -> str:
    data_repartida = data.split("_")
    return f"{data_repartida[2]}/{data_repartida[1]}/{data_repartida[0]} - {data_repartida[3]}:{data_repartida[4]}:{data_repartida[5]}"

def formato_datetime(data:str) -> datetime:
    data_repartida = data.split("_")
    return datetime(
        int(data_repartida[0]), 
        int(data_repartida[1]), 
        int(data_repartida[2]),
        int(data_repartida[3]),
        int(data_repartida[4]),
        int(data_repartida[5])
    )
