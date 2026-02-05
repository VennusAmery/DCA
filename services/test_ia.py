from services.ia_service import analizar_texto
from services.generar_pdf import guardar_pdf_con_fecha

prompt = """
Analiza este documento y:
1. Detecta nuevas normas
2. Indica fecha de publicación
3. Explica impacto jurídico
"""

ruta_txt = "storage/textos/DCA 29 enero 2026.txt"

resultado = analizar_texto(prompt, ruta_txt)

guardar_pdf_con_fecha(resultado)

print("✅ Análisis generado y guardado en PDF")
