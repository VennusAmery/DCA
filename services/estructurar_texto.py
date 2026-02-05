import re

def extraer_articulos(texto):
    patron = r"(ART[IÍ]CULO\s+\d+\.?.*)"
    partes = re.split(patron, texto, flags=re.IGNORECASE)

    articulos = []
    actual = ""

    for parte in partes:
        if re.match(patron, parte, flags=re.IGNORECASE):
            if actual:
                articulos.append(actual.strip())
            actual = parte
        else:
            actual += "\n" + parte

    if actual:
        articulos.append(actual.strip())

    return articulos
