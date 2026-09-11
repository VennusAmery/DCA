# -- limpiar_texto.py --

import re


def limpiar_texto(texto):
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    patrones_basura = [
        r"DIARIO DE CENTRO AM[ÉE]RICA.*",
        r"P[ÁA]GINA\s*\d+",
    ]

    for patron in patrones_basura:
        texto = re.sub(patron, "", texto, flags=re.IGNORECASE)

    return texto.strip()