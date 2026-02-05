import requests
from pathlib import Path

def descargar_imagen(url, nombre):
    Path("storage/images").mkdir(parents=True, exist_ok=True)

    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("No se pudo descargar")

    ruta = f"storage/images/{nombre}.jpg"
    with open(ruta, "wb") as f:
        f.write(r.content)

    return ruta