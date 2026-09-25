import re
import requests
import fitz  
from pathlib import Path

OUTPUT_DIR = "storage/pdfs"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}
_PARAM_NAMES = ["doc", "idDocumento", "verDocumento", "documento", "id"]


def _extraer_doc_id(url_o_id: str) -> str:
    """Acepta el link del visor (con cualquiera de los parametros conocidos,
    sin importar mayusculas/minusculas) o directamente el numero de documento."""
    url_o_id = url_o_id.strip()

    if url_o_id.isdigit():
        return url_o_id

    patron = r"(?:" + "|".join(_PARAM_NAMES) + r")=(\d+)"
    match = re.search(patron, url_o_id, flags=re.IGNORECASE)
    if match:
        return match.group(1)

    numeros = re.findall(r"\d{3,}", url_o_id)
    if numeros:
        return max(numeros, key=len)

    raise ValueError("No se pudo extraer el ID del documento del link.")


def _contar_paginas(contenido: bytes) -> int:
    try:
        doc = fitz.open(stream=contenido, filetype="pdf")
        n = doc.page_count
        doc.close()
        return n
    except Exception:
        return 0


def descargar_pdf_por_link(url_o_id: str, nombre_archivo: str = None) -> Path:
    doc_id = _extraer_doc_id(url_o_id)

    session = requests.Session()
    session.headers.update(HEADERS)

    url_visor = url_o_id if url_o_id.strip().lower().startswith("http") else None
    if url_visor:
        try:
            session.get(url_visor, timeout=20)
        except requests.RequestException:
            pass

    referer = url_visor or "https://legal.dca.gob.gt/"

    url_descarga = f"https://legal.dca.gob.gt/GestionDocumento/DescargarPDFDocumento?idDocumento={doc_id}"

    try:
        response = session.get(url_descarga, headers={"Referer": referer}, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"No se pudo contactar al servidor del DCA: {e}")

    if response.content[:4] != b"%PDF":
        raise ValueError(
            "El servidor del DCA no devolvio un PDF valido para este documento "
            "(posible link vencido o ID incorrecto)."
        )

    num_paginas = _contar_paginas(response.content)
    if num_paginas == 0:
        raise ValueError(
            f"El documento '{doc_id}' parece estar dañado en el servidor del DCA "
            "(incluso su propio visor no puede abrirlo). No es un error de este "
            "sistema: intenta con otra edición o vuelve a intentar más tarde."
        )

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    nombre = nombre_archivo or f"DCA manual {doc_id}.pdf"
    ruta_pdf = Path(OUTPUT_DIR) / nombre
    ruta_pdf.write_bytes(response.content)

    return ruta_pdf