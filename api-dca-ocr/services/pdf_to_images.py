# -- pdf_to_images.py --
from pdf2image import convert_from_path
import os

IMAGE_DIR = 'storage/imagenes'


def pdf_a_imagenes(pdf_path, paginas=None, dpi=300):
    """
    Convierte páginas de un PDF a imágenes PNG.

    - Si `paginas` es None, convierte el documento completo y devuelve una
      lista de tuplas (num_pagina, ruta), en orden. Esto reproduce el
      comportamiento original de la función.
    - Si `paginas` es una lista de números de página (1-indexed), solo esas
      páginas se rasterizan. Esto es lo que se debe usar en el flujo normal:
      solo hace falta convertir a imagen las páginas que no tienen texto
      nativo extraíble (es decir, las que están escaneadas), no el PDF
      completo. Ahorra tiempo de conversión y de OCR.
    """
    os.makedirs(IMAGE_DIR, exist_ok=True)
    rutas = []

    if paginas is None:
        imagenes = convert_from_path(pdf_path, dpi=dpi)
        for i, imagen in enumerate(imagenes, start=1):
            ruta = os.path.join(IMAGE_DIR, f'page_{i}.png')
            imagen.save(ruta, 'PNG')
            rutas.append((i, ruta))
        return rutas

    for num_pagina in paginas:
        # convert_from_path con first_page=last_page=num_pagina rasteriza
        # solo esa página específica, en vez de todo el documento.
        imagenes = convert_from_path(
            pdf_path, dpi=dpi, first_page=num_pagina, last_page=num_pagina
        )
        if not imagenes:
            continue
        ruta = os.path.join(IMAGE_DIR, f'page_{num_pagina}.png')
        imagenes[0].save(ruta, 'PNG')
        rutas.append((num_pagina, ruta))

    return rutas