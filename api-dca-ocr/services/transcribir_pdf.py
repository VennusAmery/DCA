# -- transcribir_pdf.py --
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
# que es una página escaneada (imagen) y se manda a OCR. 40 es un umbral
# conservador: una página real de DCA con texto nativo casi siempre tiene
# cientos de caracteres; una página en blanco o puramente gráfica no.
UMBRAL_MIN_CARACTERES = 40


def _extraer_texto_nativo(ruta_pdf):
    """
    Recorre el PDF con PyMuPDF y extrae el texto nativo de cada página
    (rápido y sin errores de reconocimiento, porque no pasa por imagen).
    Las páginas que no alcanzan el umbral mínimo de caracteres quedan
    marcadas para procesarse después con OCR — típicamente porque son
    páginas escaneadas sin capa de texto.
    """
    doc = fitz.open(ruta_pdf)
    texto_por_pagina = {}
    paginas_para_ocr = []

    for i, page in enumerate(doc, start=1):
        texto_nativo = page.get_text().strip()
        if len(texto_nativo) >= UMBRAL_MIN_CARACTERES:
            texto_por_pagina[i] = texto_nativo
        else:
            paginas_para_ocr.append(i)

    doc.close()
    return texto_por_pagina, paginas_para_ocr


def transcribir_pdf(ruta_pdf):
    """
    Extracción híbrida: usa texto nativo del PDF cuando existe, y solo
    recurre a OCR para las páginas que realmente son imágenes escaneadas.
    Esto evita el ruido de reconocimiento en las páginas que ya tenían
    texto perfecto, y reduce el tiempo total del pipeline al no rasterizar
    ni correr Tesseract sobre páginas que no lo necesitan.
    """
    ruta_pdf = Path(ruta_pdf)

    texto_por_pagina, paginas_para_ocr = _extraer_texto_nativo(ruta_pdf)

    if paginas_para_ocr:
        print(
            f"🔍 {len(paginas_para_ocr)} página(s) sin texto nativo, "
            f"aplicando OCR: {paginas_para_ocr}"
        )
        imagenes = pdf_a_imagenes(ruta_pdf, paginas=paginas_para_ocr)
        total = len(imagenes)
        for idx, (num_pagina, ruta_imagen) in enumerate(imagenes, start=1):
            print(f"🔍 OCR página {num_pagina} ({idx}/{total})")
            texto_por_pagina[num_pagina] = ocr_imagen(ruta_imagen)
    else:
        print("✅ Todas las páginas tenían texto nativo, no fue necesario OCR")

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
    para que el último PDF también se beneficie de la extracción híbrida
    (y no solo del OCR puro, como en la versión original).
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