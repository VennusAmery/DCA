import os
from pathlib import Path

import fitz  # PyMuPDF — pip install pymupdf

from services.pdf_to_images import pdf_a_imagenes
from services.ocr_service import ocr_imagen
from services.procesar_texto import procesar_texto

PDF_DIR = "storage/pdfs"
TXT_DIR = "storage/textos"
os.makedirs(TXT_DIR, exist_ok=True)

# Si una página tiene menos caracteres de texto nativo que esto, se asume
# que es una página escaneada (imagen) y se manda a OCR.
#
# IMPORTANTE: se subió de 40 a 500. El DCA a veces tiene páginas híbridas:
# una tabla lateral nativa ("EN ESTA EDICIÓN ENCONTRARÁ...") con pocas
# decenas de caracteres, PERO con el cuerpo real del acuerdo/artículo
# incrustado como IMAGEN (típico en publicaciones con membretes o
# diagramación especial). Con el umbral en 40, esa tabla lateral por sí
# sola ya "pasaba" el umbral, así que la página se marcaba como "ya tiene
# texto nativo" y jamás se mandaba a OCR — perdiendo el cuerpo completo
# del acuerdo sin ningún error visible. Una página real de DCA con
# contenido normativo completo normalmente supera los 1000-1500
# caracteres; 500 es un piso conservador que sigue exigiendo OCR en casos
# híbridos como este.
UMBRAL_MIN_CARACTERES = 500


def _pagina_tiene_imagenes(page):
    """True si la página tiene al menos una imagen incrustada. Se usa como
    señal adicional: si hay imágenes Y el texto nativo es corto, es una
    fuerte pista de que el contenido real está en la imagen, no en el
    texto nativo extraído."""
    try:
        return len(page.get_images(full=True)) > 0
    except Exception:
        return False


def _extraer_texto_nativo(ruta_pdf):
    """
    Recorre el PDF con PyMuPDF y extrae el texto nativo de cada página.
    Una página se manda a OCR si:
      (a) su texto nativo no alcanza UMBRAL_MIN_CARACTERES, o
      (b) tiene imágenes incrustadas Y su texto nativo es sospechosamente
          corto en relación a lo esperado (posible contenido oculto en
          la imagen que get_text() no puede leer).
    """
    doc = fitz.open(ruta_pdf)
    texto_por_pagina = {}
    paginas_para_ocr = []

    for i, page in enumerate(doc, start=1):
        texto_nativo = page.get_text().strip()
        tiene_imagenes = _pagina_tiene_imagenes(page)

        texto_insuficiente = len(texto_nativo) < UMBRAL_MIN_CARACTERES
        posible_contenido_en_imagen = tiene_imagenes and len(texto_nativo) < 800

        if texto_insuficiente or posible_contenido_en_imagen:
            # Guardamos el texto nativo igual (puede tener valor, ej. la
            # tabla lateral), y además la marcamos para OCR. Más abajo se
            # combinan ambos resultados en vez de descartar uno.
            if texto_nativo:
                texto_por_pagina[i] = texto_nativo
            paginas_para_ocr.append(i)
        else:
            texto_por_pagina[i] = texto_nativo

    doc.close()
    return texto_por_pagina, paginas_para_ocr


def transcribir_pdf(ruta_pdf):
    """
    Extracción híbrida: usa texto nativo del PDF cuando existe y es
    suficiente, y recurre a OCR para páginas escaneadas o híbridas
    (texto nativo corto + imágenes incrustadas). Cuando una página tiene
    AMBOS (texto nativo parcial + necesita OCR), se concatenan los dos
    resultados en vez de descartar el nativo, para no perder la tabla
    lateral ni el cuerpo del acuerdo.
    """
    ruta_pdf = Path(ruta_pdf)

    texto_por_pagina, paginas_para_ocr = _extraer_texto_nativo(ruta_pdf)

    if paginas_para_ocr:
        print(
            f"🔍 {len(paginas_para_ocr)} página(s) necesitan OCR "
            f"(texto insuficiente o posible contenido en imagen): {paginas_para_ocr}"
        )
        imagenes = pdf_a_imagenes(ruta_pdf, paginas=paginas_para_ocr)
        total = len(imagenes)
        for idx, (num_pagina, ruta_imagen) in enumerate(imagenes, start=1):
            print(f"🔍 OCR página {num_pagina} ({idx}/{total})")
            texto_ocr = ocr_imagen(ruta_imagen)

            texto_previo = texto_por_pagina.get(num_pagina, "")
            if texto_previo and texto_previo not in texto_ocr:
                # Combina lo nativo (ej. tabla lateral) con lo que
                # encontró OCR (ej. cuerpo del acuerdo en la imagen).
                texto_por_pagina[num_pagina] = f"{texto_previo}\n{texto_ocr}"
            else:
                texto_por_pagina[num_pagina] = texto_ocr
    else:
        print("✅ Todas las páginas tenían texto nativo suficiente, no fue necesario OCR")

    texto_crudo = "\n".join(texto_por_pagina[n] for n in sorted(texto_por_pagina))

    texto = procesar_texto(texto_crudo)

    salida = Path(TXT_DIR)
    salida.mkdir(parents=True, exist_ok=True)

    nombre_txt = ruta_pdf.stem + ".txt"
    ruta_txt = salida / nombre_txt

    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(texto)

    print(f"✅ Texto guardado en {ruta_txt}")

    return texto, ruta_txt


def obtener_ultimo_pdf():
    pdfs = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
    if not pdfs:
        raise FileNotFoundError("No hay PDFs en storage/pdfs")

    pdfs.sort(key=lambda f: os.path.getmtime(os.path.join(PDF_DIR, f)))
    return pdfs[-1]


def transcribir_ultimo_pdf():
    """
    Reutiliza transcribir_pdf() en vez de duplicar la lógica de extracción,
    para que el último PDF también se beneficie de la extracción híbrida.
    """
    nombre_pdf = obtener_ultimo_pdf()
    ruta_pdf = os.path.join(PDF_DIR, nombre_pdf)

    print(f"📄 Transcribiendo: {nombre_pdf}")
    texto, ruta_txt = transcribir_pdf(ruta_pdf)

    print(f"📝 Texto guardado como: {ruta_txt.name}")
    return ruta_txt.name


if __name__ == "__main__":
    pdfs_dir = Path(PDF_DIR)

    for pdf in pdfs_dir.glob("*.pdf"):
        print(f"📄 Transcribiendo: {pdf.name}")
        transcribir_pdf(pdf)