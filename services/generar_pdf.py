from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

MESES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

def guardar_pdf_con_fecha(texto):
    hoy = datetime.now()
    fecha = f"{hoy.day} {MESES[hoy.month]} {hoy.year}"

    nombre_archivo = f"DCA {fecha} - Analisis.pdf"

    Path("storage/analisis").mkdir(parents=True, exist_ok=True)
    ruta = f"storage/analisis/{nombre_archivo}"

    doc = SimpleDocTemplate(ruta, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    for linea in texto.split("\n"):
        linea = linea.strip()

        if not linea:
            story.append(Spacer(1, 12))
            continue

        linea_segura = escape(linea)
        story.append(Paragraph(linea_segura, styles["Normal"]))
        story.append(Spacer(1, 8))

    doc.build(story)
    return ruta
    