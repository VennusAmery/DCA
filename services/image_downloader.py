import requests
import os

IMAGE_DIR = 'storage/images'

def descargar_imagenes(urls):
    os.makedirs(IMAGE_DIR, exist_ok=True)

    rutas = []

    for i, url in enumerate(urls):
        response = requests.get(url)
        response.raise_for_status()

        ruta = os.path.join(IMAGE_DIR, f'page_{i+1}.png')

        with open(ruta, 'wb') as f:
            f.write(response.content)

        rutas.append(ruta)

    return rutas
