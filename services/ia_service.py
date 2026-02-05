from pathlib import Path
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analizar_texto(prompt: str, ruta_txt: str) -> str:
    texto = Path(ruta_txt).read_text(encoding="utf-8")

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "Eres analista jurídico del DCA Guatemala"},
            {"role": "user", "content": f"{prompt}\n\n{texto}"}
        ],
        temperature=0.2,
        max_completion_tokens=2000
    )

    return completion.choices[0].message.content
