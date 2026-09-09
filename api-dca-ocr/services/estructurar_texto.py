# -- estructurar_texto.py --
import re

# Anclado al inicio de línea (^ con re.MULTILINE): solo cuenta como
# encabezado de artículo si "ARTÍCULO N" aparece al comienzo de una línea.
# El patrón original no tenía esta ancla, así que hacía match con CUALQUIER
# aparición de "Artículo N" en el texto, incluyendo citas dentro de una
# oración ("conforme al Artículo 106 de la Constitución...", "según el
# Artículo 82 del Código de Trabajo..."), que son extremadamente comunes en
# redacción legal. Eso fragmentaba el documento en cada cita, no solo en
# los encabezados reales de artículo.
#
# Se permite algo de espacio/viñetas al inicio de línea (\s*[-•]?\s*) para
# tolerar pequeños artefactos de OCR antes del encabezado.
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