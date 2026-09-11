"""
reprocesar_edicion.py

Fuerza el reprocesamiento completo de UNA edición ya existente en la BD:
vuelve a transcribir (con el fix del umbral de OCR) y regenera el resumen.

Uso:
    python reprocesar_edicion.py "DCA 10 septiembre 2026.pdf"

Requiere que services/transcribir_pdf.py ya tenga el fix del umbral
(UMBRAL_MIN_CARACTERES = 500 + detección de imágenes incrustadas).
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from b2sdk.v2 import InMemoryAccountInfo, B2Api

from database import SessionLocal
from database.models import Edicion, Transcripcion, Resumen
from services.transcribir_pdf import transcribir_pdf
from services.resumen_ejecutivo import generar_resumen_ejecutivo
from services.generador_pdf import generar_pdf

PDF_DIR = Path("storage/pdfs")
RESUMENES_DIR = Path("storage/resumenes")
PDF_DIR.mkdir(parents=True, exist_ok=True)
RESUMENES_DIR.mkdir(parents=True, exist_ok=True)



# Mismo setup de autenticación que usa el pipeline original (main.py).
# El bucket es privado: una URL de b2_download_file_by_id sin el header
# de autorización correcto devuelve 401, aunque la URL en sí sea válida.
_info = InMemoryAccountInfo()
_b2_api = B2Api(_info)
_b2_api.authorize_account("production", os.getenv("B2_KEY_ID"), os.getenv("B2_APP_KEY"))


def _descargar_de_b2(url_pdf_dca, ruta_local):
    """Extrae el fileId de la URL guardada y descarga usando el SDK
    autenticado, en vez de requests.get() directo (que da 401 en bucket
    privado)."""
    if "fileId=" not in url_pdf_dca:
        raise RuntimeError(f"No se pudo extraer fileId de: {url_pdf_dca}")

    file_id = url_pdf_dca.split("fileId=")[-1]
    archivo_descargado = _b2_api.download_file_by_id(file_id)
    archivo_descargado.save_to(str(ruta_local))


def _obtener_ruta_pdf(edicion):
    """Devuelve una ruta local al PDF, descargándolo si hace falta."""
    ruta_local = PDF_DIR / edicion.nombre_archivo

    if ruta_local.exists():
        print(f"📂 Usando PDF ya presente en disco: {ruta_local}")
        return ruta_local

    if edicion.pdf_bytes:
        print("📂 Usando pdf_bytes guardado en la BD")
        ruta_local.write_bytes(edicion.pdf_bytes)
        return ruta_local

    if edicion.url_pdf_dca:
        print(f"⬇️  Descargando PDF desde Backblaze (autenticado): {edicion.url_pdf_dca}")
        _descargar_de_b2(edicion.url_pdf_dca, ruta_local)
        return ruta_local

    raise RuntimeError(
        f"No hay forma de obtener el PDF de '{edicion.nombre_archivo}' "
        "(sin archivo local, sin pdf_bytes, sin url_pdf_dca)"
    )


def reprocesar(nombre_archivo):
    db = SessionLocal()
    try:
        edicion = db.query(Edicion).filter_by(nombre_archivo=nombre_archivo).first()
        if not edicion:
            print(f"❌ No se encontró la edición '{nombre_archivo}' en la BD.")
            return

        ruta_pdf = _obtener_ruta_pdf(edicion)

        print(f"📄 Re-transcribiendo: {nombre_archivo}")
        texto_extraido, ruta_txt = transcribir_pdf(ruta_pdf)

        # Upsert de la transcripción (reemplaza si ya existía)
        if edicion.transcripcion:
            print("♻️  Reemplazando transcripción existente")
            edicion.transcripcion.texto = texto_extraido
        else:
            print("➕ Creando transcripción nueva")
            db.add(Transcripcion(edicion_id=edicion.id, texto=texto_extraido))

        edicion.estado = "transcrito"
        db.commit()

        print("📊 Regenerando resumen ejecutivo...")
        resumen_md = generar_resumen_ejecutivo(ruta_txt)

        base = Path(nombre_archivo).stem
        ruta_resumen = RESUMENES_DIR / f"{base}.md"
        ruta_resumen.write_text(resumen_md, encoding="utf-8")

        ruta_reporte = generar_pdf(resumen_md)
        nombre_reporte = Path(ruta_reporte).name
        pdf_bytes = Path(ruta_reporte).read_bytes()

        if edicion.resumen:
            print("♻️  Reemplazando resumen existente")
            edicion.resumen.contenido_md = resumen_md
            edicion.resumen.reporte_pdf = pdf_bytes
            edicion.resumen.reporte_nombre = nombre_reporte
        else:
            print("➕ Creando resumen nuevo")
            db.add(Resumen(
                edicion_id=edicion.id,
                contenido_md=resumen_md,
                reporte_pdf=pdf_bytes,
                reporte_nombre=nombre_reporte,
            ))

        edicion.estado = "resumido"
        db.commit()

        print(f"✅ Reprocesamiento completo: {nombre_archivo}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error reprocesando: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Uso: python reprocesar_edicion.py "DCA 10 septiembre 2026.pdf"')
        sys.exit(1)

    reprocesar(sys.argv[1])