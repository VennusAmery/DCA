from pathlib import Path
from database import SessionLocal
from database.models import Edicion

PDF_DIR = Path("storage/pdfs")

for archivo in PDF_DIR.iterdir():
    db = SessionLocal()
    try:
        e = db.query(Edicion).filter_by(nombre_archivo=archivo.name).first()
        if e:
            e.pdf_bytes = archivo.read_bytes()
            db.commit()
            print(f"OK: {archivo.name}")
        else:
            print(f"Sin match: {archivo.name}")
    except Exception as ex:
        db.rollback()
        print(f"ERROR {archivo.name}: {ex}")
    finally:
        db.close()