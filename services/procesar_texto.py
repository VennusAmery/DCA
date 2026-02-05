from services.limpiar_texto import limpiar_texto
from services.estructurar_texto import extraer_articulos

def procesar_texto(texto):
    limpio = limpiar_texto(texto)
    articulos = extraer_articulos(limpio)

    resultado = "📌 ARTÍCULOS\n\n"
    for art in articulos:
        resultado += art + "\n\n"

    return resultado
