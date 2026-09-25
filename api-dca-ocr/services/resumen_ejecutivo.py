# -- resumen_ejecutivo.py
import os
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------
TEXTOS_DIR = Path("storage/textos")

GEMINI_MODELOS = [
    m.strip()
    for m in os.getenv("GEMINI_MODELS", "gemini-3.6-flash").split(",")
    if m.strip()
]
GEMINI_REINTENTOS = int(os.getenv("GEMINI_RETRIES", "4"))
GEMINI_ESPERA_BASE = int(os.getenv("GEMINI_WAIT_BASE", "15"))

GROQ_MODELO = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_CHUNK_CHARS = int(os.getenv("GROQ_CHUNK_CHARS", "12000"))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "6000"))
GROQ_REINTENTOS = int(os.getenv("GROQ_RETRIES", "3"))
GROQ_ESPERA = int(os.getenv("GROQ_WAIT", "20"))

ERRORES_TEMPORALES = (
    "503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "504", "DEADLINE"
)

# ---------------------------------------------------------------
# CLIENTES
# ---------------------------------------------------------------
try:
    from google import genai
    from google.genai import types

    gemini_client = (
        genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        if os.getenv("GEMINI_API_KEY")
        else None
    )
except Exception:
    gemini_client = None
    types = None

try:
    from groq import Groq

    groq_client = (
        Groq(api_key=os.getenv("GROQ_API_KEY"))
        if os.getenv("GROQ_API_KEY")
        else None
    )
except Exception:
    groq_client = None


# ---------------------------------------------------------------
# PROMPTS
# ---------------------------------------------------------------
def _construir_prompt(texto: str) -> str:
    """
    Arma el prompt completo a partir de texto YA leído (no de una ruta).
    Antes esto vivía dentro de una función llamada 'generar_resumen_ejecutivo'
    que además nunca hacía return del prompt, y que quedaba pisada por la
    función pública de más abajo (mismo nombre) -> esto es lo que rompía
    todo el pipeline.
    """
    return f"""
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


def construir_prompt_fragmento(fragmento, i, total):
    return f"""
Eres un analista jurídico laboral de Guatemala.
Este es el fragmento {i} de {total} de una edición del Diario de Centro América (DCA).

Extrae SOLO lo relevante: leyes, decretos, acuerdos, reformas, obligaciones nuevas, multas, derechos, vigencias, fechas y entidades emisoras.
Ignora trámite, edictos, avisos comerciales y lenguaje burocrático.
Responde con un máximo de 12 viñetas cortas. Si no hay nada relevante, responde exactamente: SIN CONTENIDO RELEVANTE.

Fragmento:
{fragmento}"""


# ---------------------------------------------------------------
# UTILIDADES
# ---------------------------------------------------------------
def trocear_texto(texto, limite):
    """Divide el texto en bloques <= limite caracteres, cortando por párrafos."""
    if len(texto) <= limite:
        return [texto]

    bloques, actual = [], ""
    for parrafo in texto.split("\n"):
        # Párrafo gigante: se corta a la fuerza
        while len(parrafo) > limite:
            if actual:
                bloques.append(actual)
                actual = ""
            bloques.append(parrafo[:limite])
            parrafo = parrafo[limite:]

        if len(actual) + len(parrafo) + 1 > limite:
            bloques.append(actual)
            actual = parrafo
        else:
            actual = f"{actual}\n{parrafo}" if actual else parrafo

    if actual:
        bloques.append(actual)
    return [b for b in bloques if b.strip()]


def es_temporal(msg):
    return any(err in msg for err in ERRORES_TEMPORALES)


# ---------------------------------------------------------------
# GEMINI
# ---------------------------------------------------------------
def resumir_con_gemini(prompt):
    if not gemini_client:
        return None

    for modelo in GEMINI_MODELOS:
        for intento in range(1, GEMINI_REINTENTOS + 1):
            try:
                print(f"🤖 Gemini ({modelo}) [Intento {intento}/{GEMINI_REINTENTOS}]...")
                response = gemini_client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=32768,
                    ),
                )
                if response.text:
                    print("✅ Resumen generado con Gemini.")
                    return response.text
                print(f"⚠️ Gemini ({modelo}) devolvió respuesta vacía.")
                break

            except Exception as e:
                msg = str(e)
                if "404" in msg or "NOT_FOUND" in msg:
                    print(f"⚠️ Modelo {modelo} no existe o fue retirado.")
                    break

                if es_temporal(msg):
                    if intento < GEMINI_REINTENTOS:
                        espera = GEMINI_ESPERA_BASE * (2 ** (intento - 1))
                        print(f"⚠️ Gemini {modelo} ocupado. Esperando {espera}s...")
                        time.sleep(espera)
                    continue

                print(f"⚠️ Error con Gemini ({modelo}): {msg[:120]}")
                break

    return None


# ---------------------------------------------------------------
# GROQ
# ---------------------------------------------------------------
def llamar_groq(prompt, max_tokens):
    for intento in range(1, GROQ_REINTENTOS + 1):
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODELO,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            msg = str(e)
            if ("429" in msg or "rate_limit" in msg) and intento < GROQ_REINTENTOS:
                print(f"⚠️ Groq límite de tasa. Esperando {GROQ_ESPERA}s...")
                time.sleep(GROQ_ESPERA)
                continue
            raise


def resumir_con_groq(texto):
    if not groq_client:
        return None

    print(f"🚀 Respaldo con Groq ({GROQ_MODELO})...")
    try:
        fragmentos = trocear_texto(texto, GROQ_CHUNK_CHARS)

        if len(fragmentos) == 1:
            resultado = llamar_groq(_construir_prompt(texto), GROQ_MAX_TOKENS)
        else:
            print(f"📚 Texto largo: {len(fragmentos)} fragmentos (map-reduce).")
            notas = []
            for i, frag in enumerate(fragmentos, 1):
                print(f"   ↳ Fragmento {i}/{len(fragmentos)}")
                nota = llamar_groq(
                    construir_prompt_fragmento(frag, i, len(fragmentos)), 900
                ).strip()
                if nota and "SIN CONTENIDO RELEVANTE" not in nota:
                    notas.append(f"[Fragmento {i}]\n{nota}")

            if not notas:
                raise RuntimeError("Groq no encontró contenido relevante.")

            condensado = "\n\n".join(notas)
            resultado = llamar_groq(_construir_prompt(condensado), GROQ_MAX_TOKENS)

        print("✅ Resumen generado con Groq.")
        return resultado

    except Exception as e:
        print(f"❌ Error al ejecutar Groq: {e}")
        return None


# ---------------------------------------------------------------
# FUNCIÓN PÚBLICA
# ---------------------------------------------------------------
def generar_resumen_ejecutivo(ruta_txt):
    texto = Path(ruta_txt).read_text(encoding="utf-8", errors="ignore")

    resultado = resumir_con_gemini(_construir_prompt(texto))
    if resultado:
        return resultado

    print("🚀 Gemini no disponible. Activando respaldo Groq...")
    resultado = resumir_con_groq(texto)
    if resultado:
        return resultado

    raise RuntimeError("❌ Fallaron Gemini y el respaldo Groq.")