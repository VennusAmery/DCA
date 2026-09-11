import os
from pdf2image import convert_from_path

IMAGE_DIR = 'storage/imagenes'
POPPLER_PATH = os.getenv(
    "POPPLER_PATH", 
    r"D:\libreria\Release-26.07.0-0\poppler-26.07.0\Library\bin"
)
TESSERACT_CMD = os.getenv(
    "TESSERACT_CMD", 
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def pdf_a_imagenes(pdf_path, paginas=None, dpi=300):
    os.makedirs(IMAGE_DIR, exist_ok=True)
    rutas = []

    # Si no se pasan páginas específicas, se convierte todo el PDF
    if paginas is None:
        imagenes = convert_from_path(
            pdf_path, 
            dpi=dpi, 
            poppler_path=POPPLER_PATH
        )
        for idx, img in enumerate(imagenes, start=1):
            ruta = os.path.join(IMAGE_DIR, f'page_{idx}.png')
            img.save(ruta, 'PNG')
            rutas.append((idx, ruta))
        return rutas

    # Si se pasa un listado de páginas específicas (ej. [2, 3, 4, ...])
    for num_pagina in paginas:
        imagenes = convert_from_path(
            pdf_path, 
            dpi=dpi, 
            first_page=num_pagina, 
            last_page=num_pagina,
            poppler_path=POPPLER_PATH  # <--- Agregado aquí también
        )
        if not imagenes:
            continue
        ruta = os.path.join(IMAGE_DIR, f'page_{num_pagina}.png')
        imagenes[0].save(ruta, 'PNG')
        rutas.append((num_pagina, ruta))

    return rutas