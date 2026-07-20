# -- control_descargas.py --

import json
from pathlib import Path

REGISTRO = Path("storage/registro.json")

def cargar_registro():
    if not REGISTRO.exists() or REGISTRO.stat().st_size == 0:
        return {}  
    try:
        return json.loads(REGISTRO.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}  
    
def guardar_registro(data):
    REGISTRO.write_text(json.dumps(data, indent=2), encoding="utf-8")

def ya_procesado(nombre_pdf):
    data = cargar_registro()
    lista_procesados = data.get("procesados", [])
    return nombre_pdf in lista_procesados

def marcar_procesado(nombre_pdf):
    data = cargar_registro()
    if "procesados" not in data:
        data["procesados"] = []
    
    if nombre_pdf not in data["procesados"]:
        data["procesados"].append(nombre_pdf)
        REGISTRO.write_text(json.dumps(data, indent=4), encoding="utf-8")