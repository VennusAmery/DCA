from services.dca_scraper import obtener_imagenes_dca

url = 'https://legal.dca.gob.gt/'
imagenes = obtener_imagenes_dca(url)

for img in imagenes:
    print(img)
