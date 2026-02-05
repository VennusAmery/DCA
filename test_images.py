from services.dca_scraper import obtener_imagenes_dca
from services.image_downloader import descargar_imagenes

url = 'https://legal.dca.gob.gt/'
imagenes = obtener_imagenes_dca(url)
rutas = descargar_imagenes(imagenes)

print(rutas)
