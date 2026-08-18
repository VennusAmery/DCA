"""
migrar_archivos_a_db.py

Lee storage/mapa.json + archivos locales y los inserta en MySQL.
Correr una sola vez.
"""
from pathlib import Path
from datetime import date
import json

from database import SessionLocal
from database.models import Edicion, Transcripcion, Resumen
from utils_fecha import extraer_fecha

MAPA_PATH = Path("storage/mapa.json")
TXT_DIR = Path("storage/textos")
RESUMENES_DIR = Path("storage/resumenes")
REPORTES_DIR = Path("storage/reportes")


def cargar_mapa():
    if not MAPA_PATH.exists():
        print("No existe mapa.json, nada que migrar.")
        return {}
    return json.loads(MAPA_PATH.read_text(encoding="utf-8"))


def migrar():
    mapa = cargar_mapa()
    db = SessionLocal()
    migrados = 0
    saltados = 0

    try:
        for base, entrada in mapa.items():
            nombre_archivo = f"{base}.pdf"

            ya_existe = db.query(Edicion).filter_by(nombre_archivo=nombre_archivo).first()
            if ya_existe:
                print(f"Ya existe, se salta: {nombre_archivo}")
                saltados += 1
                continue

            fecha = extraer_fecha(nombre_archivo) or date.today().isoformat()

            texto = ""
            ruta_txt = TXT_DIR / f"{base}.txt"
            if ruta_txt.exists():
                texto = ruta_txt.read_text(encoding="utf-8")

            resumen_md = ""
            nombre_resumen = entrada.get("resumen")
            if nombre_resumen:
                ruta_resumen = RESUMENES_DIR / nombre_resumen
                if ruta_resumen.is_file():
                    resumen_md = ruta_resumen.read_text(encoding="utf-8")

            pdf_bytes = None
            nombre_reporte = entrada.get("reporte")
            if nombre_reporte:
                ruta_reporte = REPORTES_DIR / nombre_reporte
                if ruta_reporte.is_file():
                    pdf_bytes = ruta_reporte.read_bytes()

            edicion = Edicion(
                nombre_archivo=nombre_archivo,
                fecha_publicacion=fecha,
                estado="resumido" if pdf_bytes else "transcrito",
            )
            db.add(edicion)
            db.flush()  # para obtener edicion.id

            if texto:
                db.add(Transcripcion(edicion_id=edicion.id, texto=texto))

            if resumen_md or pdf_bytes:
                db.add(Resumen(
                    edicion_id=edicion.id,
                    contenido_md=resumen_md,
                    reporte_pdf=pdf_bytes,
                    reporte_nombre=nombre_reporte,
                ))

            db.commit()
            migrados += 1
            print(f"Migrado: {nombre_archivo}")

    except Exception as e:
        db.rollback()
        print(f"Error migrando: {e}")
    finally:
        db.close()

    print(f"\nListo. Migrados: {migrados}. Saltados: {saltados}.")


if __name__ == "__main__":
    migrar()