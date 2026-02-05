from pathlib import Path

def cargar_texto_transcrito(pdf_path):
    txt_path = Path("storage/textos") / (pdf_path.stem + ".txt")

    if not txt_path.exists():
        raise FileNotFoundError(f"No existe el texto transcrito para {pdf_path.name}")

    return txt_path.read_text(encoding="utf-8")
