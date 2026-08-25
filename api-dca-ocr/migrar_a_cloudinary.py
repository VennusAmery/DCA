# migrar_a_b2.py
import os
from dotenv import load_dotenv
load_dotenv()

from b2sdk.v2 import InMemoryAccountInfo, B2Api
from database import SessionLocal
from database.models import Edicion

info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", os.getenv("B2_KEY_ID"), os.getenv("B2_APP_KEY"))

bucket_name = os.getenv("B2_BUCKET_NAME")
bucket = b2_api.get_bucket_by_name(bucket_name)

ediciones = SessionLocal().query(Edicion).filter(Edicion.pdf_bytes.isnot(None)).all()

for e in ediciones:
    db = SessionLocal()
    try:
        edicion = db.query(Edicion).filter_by(id=e.id).first()
        if not edicion.pdf_bytes:
            continue

        print(f"Subiendo: {edicion.nombre_archivo}")

        nombre_archivo_b2 = f"dca/{edicion.nombre_archivo}"

        archivo_subido = bucket.upload_bytes(
            edicion.pdf_bytes,
            nombre_archivo_b2
        )

        download_url = b2_api.get_download_url_for_fileid(archivo_subido.id_)

        edicion.url_pdf_dca = download_url
        edicion.pdf_bytes = None
        db.commit()
        print(f"OK: {download_url}")

    except Exception as ex:
        db.rollback()
        print(f"ERROR {edicion.nombre_archivo}: {ex}")
    finally:
        db.close()

print("Migración completa")