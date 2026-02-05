from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

PDF_DIR = Path("storage/pdfs")

app.mount("/pdfs", StaticFiles(directory=PDF_DIR), name="pdfs")
