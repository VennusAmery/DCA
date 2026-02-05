import requests
import os
from datetime import datetime
from pathlib import Path

def descargar_pdf_dca():
    PDF_URL = "https://legal.dca.gob.gt/Content/PDF/DocumentoDelDiaPdf.pdf"
    OUTPUT_DIR = "storage/pdfs"
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # ---- FECHA ACTUAL ----
    MESES_ES = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    hoy = datetime.now()
    dia = hoy.day
    mes = MESES_ES[hoy.month - 1]
    anio = hoy.year

    nombre_archivo = f"DCA {dia} {mes} {anio}.pdf"
    pdf_path = Path(OUTPUT_DIR) / nombre_archivo

    # ---- HEADERS PARA EVITAR 403 ----
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://legal.dca.gob.gt/"
    }

    # ---- DESCARGA ----
    response = requests.get(PDF_URL, headers=headers)
    response.raise_for_status()

    with open(pdf_path, "wb") as f:
        f.write(response.content)

    print(f"📄 PDF del DCA guardado como: {nombre_archivo}")
    return pdf_path
