"""
auto_dca.py
"""
from pathlib import Path
import json

from services.download_pdf import descargar_pdf_dca
from services.control_descargas import ya_procesado, marcar_procesado
from services.transcribir_pdf import transcribir_pdf
from services.resumen_ejecutivo import generar_resumen_ejecutivo
print("IMPORTACIÓN COMPLETADA")

from services.generador_pdf import generar_pdf

import requests

MAPA_PATH = Path("storage/mapa.json")
RESUMENES_DIR = Path("storage/resumenes")


def _cargar_mapa():
    if not MAPA_PATH.exists():
        return {}
    try:
        return json.loads(MAPA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _guardar_en_mapa(base: str, reporte_nombre: str, resumen_nombre: str):
    mapa = _cargar_mapa()
    mapa[base] = {"reporte": reporte_nombre, "resumen": resumen_nombre}
    MAPA_PATH.parent.mkdir(parents=True, exist_ok=True)
    MAPA_PATH.write_text(json.dumps(mapa, indent=2, ensure_ascii=False), encoding="utf-8")


def _enviar_a_lumes(texto: str, nombre_pdf: str):
    """Entrega el texto procesado al pipeline de LUMES."""
    try:
        res = requests.post(
            "http://localhost:3000/api/dca/procesar",
            json={
                "texto":      texto,
                "nombre_pdf": nombre_pdf,
                "fuente":     "DCA"
            },
            timeout=30
        )
        print(f"[LUMES] Texto enviado → {res.status_code}")
    except Exception as e:
        print(f"[LUMES] Error al enviar: {e}")


def ejecutar_automatico():
    ruta_pdf = descargar_pdf_dca()

    if not ruta_pdf:
        return

    nombre = ruta_pdf.name
    base = ruta_pdf.stem

    if ya_procesado(nombre):
        print(f"🔁 El archivo '{nombre}' ya fue procesado. Abortando.")
        return

    print("📄 Transcribiendo PDF...")
    texto_extraido, ruta_txt = transcribir_pdf(ruta_pdf)
    # función de envío
    # _enviar_a_lumes(texto_extraido, nombre)

    marcar_procesado(nombre)

    try:
        print("📊 Generando resumen ejecutivo...")
        resumen = generar_resumen_ejecutivo(ruta_txt)

        RESUMENES_DIR.mkdir(parents=True, exist_ok=True)
        ruta_resumen = RESUMENES_DIR / f"{base}.md"
        ruta_resumen.write_text(resumen, encoding="utf-8")

        ruta_reporte = generar_pdf(resumen)
        nombre_reporte = Path(ruta_reporte).name

        _guardar_en_mapa(base, nombre_reporte, ruta_resumen.name)

        print(f"📄 PDF generado: {ruta_reporte}")

    except Exception as e:
        print(f"Error generando resumen ejecutivo: {e}")

    print(f"✅ Proceso completo y registrado: {nombre}")


if __name__ == "__main__":
    ejecutar_automatico()