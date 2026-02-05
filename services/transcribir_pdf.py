import os
from services.pdf_to_images import pdf_a_imagenes
from services.ocr_service import ocr_imagenes
from services.procesar_texto import procesar_texto
import sys
from pathlib import Path

def transcribir_pdf(ruta_pdf):
    imagenes = pdf_a_imagenes(ruta_pdf)
    texto_crudo = ocr_imagenes(imagenes)
    texto = procesar_texto(texto_crudo)

    salida = Path("storage/textos")
    salida.mkdir(exist_ok=True)

    nombre_txt = ruta_pdf.stem + ".txt"
    ruta_txt = salida / nombre_txt

    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(texto)

    print(f"✅ Texto guardado en {ruta_txt}")
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

PDF_DIR = "storage/pdfs"
TXT_DIR = "storage/textos"

os.makedirs(TXT_DIR, exist_ok=True)

def obtener_ultimo_pdf():
    pdfs = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
    if not pdfs:
        raise FileNotFoundError("No hay PDFs en storage/pdfs")

    pdfs.sort(key=lambda f: os.path.getmtime(os.path.join(PDF_DIR, f)))
    return pdfs[-1]

def transcribir_ultimo_pdf():
    nombre_pdf = obtener_ultimo_pdf()
    ruta_pdf = os.path.join(PDF_DIR, nombre_pdf)

    print(f"📄 Transcribiendo: {nombre_pdf}")

    imagenes = pdf_a_imagenes(ruta_pdf)
    texto = ocr_imagenes(imagenes)

    nombre_txt = nombre_pdf.replace(".pdf", ".txt")
    ruta_txt = os.path.join(TXT_DIR, nombre_txt)

    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(texto)

    print(f"📝 Texto guardado como: {nombre_txt}")
    return nombre_txt

if __name__ == "__main__":
    from pathlib import Path

    pdfs_dir = Path("storage/pdfs")

    for pdf in pdfs_dir.glob("*.pdf"):
        print(f"📄 Transcribiendo: {pdf.name}")
        transcribir_pdf(pdf)

