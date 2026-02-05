import re

def limpiar_texto(texto):
    # Quitar múltiples espacios
    texto = re.sub(r"[ \t]+", " ", texto)

    # Quitar líneas vacías repetidas
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    # Quitar encabezados típicos del DCA
    patrones_basura = [
        r"DIARIO DE CENTRO AMERICA.*",
        r"Página \d+",
    ]

    for patron in patrones_basura:
        texto = re.sub(patron, "", texto, flags=re.IGNORECASE)

    return texto.strip()
