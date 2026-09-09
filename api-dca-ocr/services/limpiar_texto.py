# -- limpiar_texto.py --

import re


def limpiar_texto(texto):
    # Quitar múltiples espacios
    texto = re.sub(r"[ \t]+", " ", texto)

    # Quitar líneas vacías repetidas
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    # Quitar encabezados típicos del DCA. re.IGNORECASE cubre mayúsculas/
    # minúsculas pero no acentos, y el OCR es inconsistente reconociendo
    # tildes ("AMÉRICA" vs "AMERICA"). Se usa [ÉE] para tolerar ambas
    # variantes sin depender de que el OCR acierte el acento.
    patrones_basura = [
        r"DIARIO DE CENTRO AM[ÉE]RICA.*",
        r"P[ÁA]GINA\s*\d+",
    ]

    for patron in patrones_basura:
        texto = re.sub(patron, "", texto, flags=re.IGNORECASE)

    return texto.strip()