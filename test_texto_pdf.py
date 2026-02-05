from services.extract_text import extraer_texto_pdf

texto = extraer_texto_pdf("storage/pdfs/documento_del_dia.pdf")

if texto:
    print("📄 TEXTO DETECTADO:\n")
    print(texto[:1500])
else:
    print("❌ NO hay texto real en el PDF")
