import json


def save_write_json(path, tipo:str, conteudo:dict|list=dict()) -> None|dict:
    with path.open(tipo, encoding="utf-8") as f:
        if tipo == 'w':
            json.dump(conteudo, f, indent=4, ensure_ascii=False)
        else:
            dados = json.load(f)
            return dados

def get_json_files(path) -> dict:
    dicio = {}
    for file in path.iterdir():
        with file.open('r', encoding="utf-8") as f:
            dicio[file.name] = json.load(f)
    return dicio
