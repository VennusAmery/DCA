# migrar_a_cloudinary.py
import os
from dotenv import load_dotenv
load_dotenv()

import cloudinary
import cloudinary.uploader
from database import SessionLocal
from database.models import Edicion

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

ediciones = SessionLocal().query(Edicion).filter(Edicion.pdf_bytes.isnot(None)).all()

for e in ediciones:
    db = SessionLocal()
    try:
        edicion = db.query(Edicion).filter_by(id=e.id).first()
        if not edicion.pdf_bytes:
            continue

        print(f"Subiendo: {edicion.nombre_archivo}")

        resultado = cloudinary.uploader.upload(
            edicion.pdf_bytes,
            resource_type="raw",
            public_id=f"dca/{edicion.nombre_archivo.replace('.pdf','')}",
            overwrite=True
        )

        edicion.url_pdf_dca = resultado['secure_url']
        edicion.pdf_bytes = None
        db.commit()
        print(f"OK: {resultado['secure_url']}")

    except Exception as ex:
        db.rollback()
        print(f"ERROR {edicion.nombre_archivo}: {ex}")
    finally:
        db.close()

print("Migración completa")