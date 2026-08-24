"""
auto_dca.py
"""
import os
from pathlib import Path
from datetime import date
import json

from dotenv import load_dotenv
load_dotenv()

from services.download_pdf import descargar_pdf_dca
from services.control_descargas import marcar_procesado
from services.transcribir_pdf import transcribir_pdf
from services.resumen_ejecutivo import generar_resumen_ejecutivo
print("IMPORTACIÓN COMPLETADA")

from services.generador_pdf import generar_pdf

import requests

from database import SessionLocal
from database.models import Edicion, Transcripcion, Resumen

import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

MAPA_PATH = Path("storage/mapa.json")
RESUMENES_DIR = Path("storage/resumenes")

import fitz

def comprimir_pdf(ruta_pdf):
    ruta_temp = ruta_pdf.with_suffix(".tmp.pdf")
    doc = fitz.open(ruta_pdf)
    doc.save(ruta_temp, garbage=4, deflate=True)
    doc.close()
    ruta_temp.replace(ruta_pdf)

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

def ejecutar_automatico():
    ruta_pdf = descargar_pdf_dca()

    if not ruta_pdf:
        return

    nombre = ruta_pdf.name
    base = ruta_pdf.stem

    db = SessionLocal()
    edicion = None

    try:
        ya_existe = db.query(Edicion).filter_by(nombre_archivo=nombre).first()
        if ya_existe:
            print(f"🔁 El archivo '{nombre}' ya está en la base de datos. Abortando.")
            return

        edicion = Edicion(
            nombre_archivo=nombre,
            fecha_publicacion=date.today(),
            estado="descargado",
        )
        db.add(edicion)
        db.commit()
        db.refresh(edicion)

        comprimir_pdf(ruta_pdf)

        print("☁️ Subiendo PDF a Cloudinary...")
        resultado = cloudinary.uploader.upload(
            str(ruta_pdf),
            resource_type="raw",
            public_id=f"dca/{base}",
            overwrite=True
        )
        edicion.url_pdf_dca = resultado['secure_url']
        db.commit()
        print(f"✅ PDF subido: {edicion.url_pdf_dca}")

        print("📄 Transcribiendo PDF...")
        texto_extraido, ruta_txt = transcribir_pdf(ruta_pdf)

        db.add(Transcripcion(edicion_id=edicion.id, texto=texto_extraido))
        edicion.estado = "transcrito"
        db.commit()

        marcar_procesado(nombre)

        print("📊 Generando resumen ejecutivo...")
        resumen = generar_resumen_ejecutivo(ruta_txt)

        RESUMENES_DIR.mkdir(parents=True, exist_ok=True)
        ruta_resumen = RESUMENES_DIR / f"{base}.md"
        ruta_resumen.write_text(resumen, encoding="utf-8")

        ruta_reporte = generar_pdf(resumen)
        nombre_reporte = Path(ruta_reporte).name
        pdf_bytes = Path(ruta_reporte).read_bytes()

        db.add(Resumen(
            edicion_id=edicion.id,
            contenido_md=resumen,
            reporte_pdf=pdf_bytes,
            reporte_nombre=nombre_reporte,
        ))
        edicion.estado = "resumido"
        db.commit()

        _guardar_en_mapa(base, nombre_reporte, ruta_resumen.name)

        print(f"📄 PDF generado: {ruta_reporte}")
        print(f"✅ Proceso completo y registrado: {nombre}")

    except Exception as e:
        db.rollback()
        if edicion is not None:
            edicion.estado = "error"
            db.commit()
        print(f"Error en el pipeline: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    ejecutar_automatico()