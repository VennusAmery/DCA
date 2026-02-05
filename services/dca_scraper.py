import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://legal.dca.gob.gt'

def obtener_imagenes_dca(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    imagenes = []

    for img in soup.find_all('img'):
        src = img.get('src')

        if not src:
            continue

        if src.startswith('/'):
            src = BASE_URL + src

        if 'dca' in src.lower():
            imagenes.append(src)

    if not imagenes:
        raise Exception('No se encontraron imágenes del diario')

    return imagenes
