from services.download_pdf import descargar_pdf_dca
from services.control_descargas import ya_procesado, marcar_procesado
from services.transcribir_pdf import transcribir_pdf

def ejecutar_automatico():
    ruta_pdf = descargar_pdf_dca()
    if not ruta_pdf: 
        return
    
    nombre = ruta_pdf.name

    if ya_procesado(nombre):
        print(f"🔁 El archivo '{nombre}' ya fue procesado anteriormente. Abortando.")
        return

    print("📄 Transcribiendo PDF...")
    transcribir_pdf(ruta_pdf)

    marcar_procesado(nombre)
    print(f"✅ Proceso completo y registrado: {nombre}")

if __name__ == "__main__":
    ejecutar_automatico()