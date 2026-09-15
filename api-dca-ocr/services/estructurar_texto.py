# -- estructurar_texto.py --
import re

PATRON_ARTICULO = r"^\s*[-•]?\s*(ART[IÍ]CULO\s+\d+\.?)"


def extraer_articulos(texto):
    partes = re.split(PATRON_ARTICULO, texto, flags=re.IGNORECASE | re.MULTILINE)

    articulos = []
    actual = ""

    for parte in partes:
        es_encabezado = re.match(
            PATRON_ARTICULO, parte, flags=re.IGNORECASE | re.MULTILINE
        )
        if es_encabezado:
            if actual.strip():
                articulos.append(actual.strip())
            actual = parte
        else:
            actual += "\n" + parte

    if actual.strip():
        articulos.append(actual.strip())

    return articulos