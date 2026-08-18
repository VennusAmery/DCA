import re

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}


def extraer_fecha(nombre_archivo: str):
    """
    Extrae la fecha de nombres tipo 'DCA 27 enero 2026.pdf'.
    Devuelve 'YYYY-MM-DD' o None si no encuentra patrón.
    """
    patron = re.search(
        r"(\d{1,2})\s+de\s+([a-záéíóú]+)\s+(\d{4})|(\d{1,2})\s+([a-záéíóú]+)\s+(\d{4})",
        nombre_archivo.lower(),
    )
    if not patron:
        return None

    if patron.group(1):
        dia, mes_txt, anio = patron.group(1), patron.group(2), patron.group(3)
    else:
        dia, mes_txt, anio = patron.group(4), patron.group(5), patron.group(6)

    mes = MESES.get(mes_txt)
    if not mes:
        return None

    return f"{anio}-{mes:02d}-{int(dia):02d}"
