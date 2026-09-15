import os
import pymupdf  # Reemplaza pdf2image y elimina la necesidad de POPPLER_PATH

IMAGE_DIR = 'storage/imagenes'

def pdf_a_imagenes(pdf_path, paginas=None, dpi=300):
    os.makedirs(IMAGE_DIR, exist_ok=True)
    rutas = []
    
    # Abrir el PDF con PyMuPDF
    doc = pymupdf.open(pdf_path)

    # Si no se pasan páginas específicas, se convierte todo el PDF
    if paginas is None:
        for idx in range(len(doc)):
            page = doc.load_page(idx)
            pix = page.get_pixmap(dpi=dpi)
            
            num_pagina = idx + 1
            ruta = os.path.join(IMAGE_DIR, f'page_{num_pagina}.png')
            pix.save(ruta)
            rutas.append((num_pagina, ruta))
        doc.close()
        return rutas

    # Si se pasa un listado de páginas específicas (ej. [2, 3, 4, ...])
    for num_pagina in paginas:
        # PyMuPDF usa índices base 0 (Página 1 = índice 0)
        idx = num_pagina - 1
        
        # Validar que la página exista dentro del rango del PDF
        if idx < 0 or idx >= len(doc):
            continue

        page = doc.load_page(idx)
        pix = page.get_pixmap(dpi=dpi)
        
        ruta = os.path.join(IMAGE_DIR, f'page_{num_pagina}.png')
        pix.save(ruta)
        rutas.append((num_pagina, ruta))

    doc.close()
    return rutas