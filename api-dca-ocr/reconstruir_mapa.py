"""
Reconstruye storage/mapa.json buscando, por fecha, los reportes PDF
que ya existen en storage/reportes/ y conectándolos con las ediciones
registradas en storage/registro.json.

Correr una sola vez:
    python reconstruir_mapa.py
"""
import json
import re
from pathlib import Path

REGISTRO = Path("storage/registro.json")
REPORTES_DIR = Path("storage/reportes")
MAPA_PATH = Path("storage/mapa.json")

MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12",
}


def _fecha_numerica(base_nombre: str):
    """'DCA 13 julio 2026' -> '13 07 2026'"""
    m = re.search(r"(\d{1,2})\s+([a-záéíóú]+)\s+(\d{4})", base_nombre.lower())
    if not m:
        return None
    dia, mes_txt, anio = m.groups()
    mes = MESES.get(mes_txt)
    if not mes:
        return None
    return f"{int(dia):02d} {mes} {anio}"


def main():
    registro = json.loads(REGISTRO.read_text(encoding="utf-8"))
    procesados = registro.get("procesados", [])

    mapa = {}
    if MAPA_PATH.exists():
        mapa = json.loads(MAPA_PATH.read_text(encoding="utf-8"))

    reportes = list(REPORTES_DIR.glob("*.pdf"))

    for nombre in procesados:
        base = Path(nombre).stem
        if base in mapa:
            continue

        fecha = _fecha_numerica(base)
        if not fecha:
            print(f"⚠ No se pudo leer fecha de: {base}")
            continue

        encontrado = None
        for r in reportes:
            if fecha in r.name:
                encontrado = r
                break

        if encontrado:
            mapa[base] = {"reporte": encontrado.name, "resumen": ""}
            print(f"✅ {base} -> {encontrado.name}")
        else:
            print(f"✗ Sin reporte para: {base}")

    MAPA_PATH.write_text(json.dumps(mapa, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGuardado en {MAPA_PATH}")


if __name__ == "__main__":
    main()
