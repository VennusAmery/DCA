from pdf2image import convert_from_path
import os

IMAGE_DIR = 'storage/imagenes'

def pdf_a_imagenes(pdf_path):
    os.makedirs(IMAGE_DIR, exist_ok=True)

    paginas = convert_from_path(pdf_path, dpi=300)
    rutas = []

    for i, pagina in enumerate(paginas):
        ruta = os.path.join(IMAGE_DIR, f'page_{i+1}.png')
        pagina.save(ruta, 'PNG')
        rutas.append(ruta)

    return rutas


POPPLER_PATH = r"D:\Release-25.12.0-0\poppler-25.12.0\Library\bin"

def pdf_a_imagenes(pdf_path):
    paginas = convert_from_path(
        pdf_path,
        dpi=300,
        poppler_path=POPPLER_PATH
    )
    return paginas
