import os
import platform
import cv2
import pytesseract

_RUTA_POR_DEFECTO_WINDOWS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
_RUTA_POR_DEFECTO_LINUX = "/usr/bin/tesseract"

ruta_tesseract = os.getenv("TESSERACT_CMD")

if not ruta_tesseract:
    if platform.system() == "Windows":
        ruta_tesseract = _RUTA_POR_DEFECTO_WINDOWS
    else:
        ruta_tesseract = _RUTA_POR_DEFECTO_LINUX

pytesseract.pytesseract.tesseract_cmd = ruta_tesseract


def _preprocesar(ruta_imagen):
    """
    Convierte a escala de grises, aplica un desenfoque suave para reducir
    ruido de escaneo, y binariza con el método de Otsu en vez de un umbral
    fijo. Otsu calcula el punto de corte óptimo según el histograma de cada
    imagen, lo que maneja mucho mejor variaciones de iluminación, sellos,
    membretes o fondos con textura que un umbral fijo (ej. `< 180`) suele
    arruinar (volviendo ilegible texto sobre fondo gris, o borrando texto
    tenue).
    """
    img = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    _, binaria = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binaria


def ocr_imagen(ruta_imagen, psm=3):
    """
    OCR de una sola imagen/página.

    psm=3 (segmentación automática de página completa) reemplaza al psm=6
    original (bloque uniforme de texto). El DCA tiene columnas, tablas y
    encabezados; psm=6 tiende a mezclar el orden del texto entre columnas,
    lo que rompe el sentido de las oraciones (y por lo tanto la detección
    de términos como "salario mínimo" o "Código de Trabajo", que dependen
    de que las palabras queden en el orden correcto).
    """
    img = _preprocesar(ruta_imagen)
    config = f"--psm {psm}"
    return pytesseract.image_to_string(img, lang="spa", config=config)


def ocr_imagenes(imagenes, psm=3):
    """
    Acepta tanto una lista de rutas (comportamiento original) como una lista
    de tuplas (num_pagina, ruta) — que es lo que ahora devuelve
    pdf_a_imagenes() cuando se le pasan páginas específicas — para no romper
    otros lugares del código que todavía llamen a esta función con el
    formato viejo.
    """
    texto_total = ""
    total = len(imagenes)

    for i, item in enumerate(imagenes, start=1):
        ruta = item[1] if isinstance(item, tuple) else item
        print(f"🔍 OCR página {i}/{total} ({int(i / total * 100)}%)")
        texto_total += ocr_imagen(ruta, psm=psm) + "\n"

    print("✅ OCR completado")
    return texto_total