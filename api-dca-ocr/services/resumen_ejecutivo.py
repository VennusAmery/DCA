from dotenv import load_dotenv
from pathlib import Path
import os
import google.generativeai as genai

TEXTOS_DIR = Path("storage/textos")

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generar_resumen_ejecutivo(ruta_txt):

    texto = Path(ruta_txt).read_text(
        encoding="utf-8",
        errors="ignore"
    )

    model = genai.GenerativeModel(
        "models/gemini-2.5-flash"
    )


    prompt = f"""
Eres un consultor jurídico estratégico especializado en legislación laboral y decretos de Guatemala. 

Tu tarea es leer TODO el documento del Diario de Centro América (DCA) provisto, pero NO debes resumir artículo por artículo. En su lugar, realiza un análisis ejecutivo de alto valor enfocado en el impacto real.

Sigue estas directrices:
1. Identifica el núcleo: Explica con claridad de qué trata la nueva ley o acuerdo en general, su propósito y a quiénes afecta principalmente.
2. Filtra lo irrelevante: Omite artículos de trámite, transitorios menores o lenguaje puramente burocrático.
3. Destaca lo sobresaliente: Enfócate ÚNICAMENTE en los artículos más importantes, revolucionarios o críticos (reformas clave, nuevas obligaciones pesadas, multas severas o cambios de derechos).
4. Sé conciso pero sustancioso: Agrupa la información por impacto temático para que sea una lectura ágil pero sumamente informativa.

 REGLA DE FORMATO CRÍTICA: Debes escribir los títulos EXACTAMENTE como se muestran abajo. 
- Deben empezar SIEMPRE con el doble hashtag '## '.
- NO les agregues números al principio (NUNCA escribas '01-' o '1.'). 
- Respeta las mayúsculas y minúsculas exactas. Si no cumples esto, el sistema fallará.

## Panorama General
(Resumen directo de qué trata la nueva ley, quién la emite, cuál es su objetivo principal en el contexto de Guatemala y su alcance general).

## Aspectos Relevantes
(Presenta un análisis de los artículos más sobresalientes y críticos. Explica qué cambia de forma contundente en comparación con el pasado).

## Impacto Jurídico
(Resumen de los cambios normativos esenciales: qué leyes o artículos importantes se modifican, derogan o se crean).

## Para No Juristas
(Explicación ejecutiva y en lenguaje cotidiano de lo más importante que debe saber un ciudadano, trabajador o empresario en su día a día).

## Para Juristas
(Análisis técnico condensado del núcleo del decreto: base constitucional, considerandos clave y vigencia).

## Recomendaciones
(Lista de acciones clave y prioritarias que deben tomar los afectados para adaptarse rápido a lo más importante de la norma).

## Conclusión
(Un cierre breve sobre el impacto real que tendrá esta publicación en el ecosistema legal guatemalteco).

## Panorama de Noticias
(Si hay múltiples acuerdos o leyes en el DCA, lista de forma muy ejecutiva mediante subtítulos '###' de qué trata cada uno, destacando solo su esencia sin profundizar de más).

## Glosario Técnico
(Define brevemente solo los términos o conceptos más importantes y necesarios para entender este resumen utilizando el formato '**Término** - Definición').

## Sumario General
(Un índice resumido con subtítulos '###' que refleje los bloques clave analizados en este reporte).

Documento original del DCA a analizar:
{texto}"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.2, # Un pelín más arriba para que redacte de forma más fluida y resumida
            "max_output_tokens": 8192 # Espacio de sobra para una gran respuesta ejecutiva
        }
    )

    return response.text