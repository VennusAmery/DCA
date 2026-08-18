# -- ocr_service.py --

from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def ocr_imagenes(imagenes):
    texto_total = ""
    total = len(imagenes)

    for i, img in enumerate(imagenes, start=1):
        print(f"🔍 OCR página {i}/{total} ({int(i/total*100)}%)")

        img = Image.open(img).convert("L")
        img = img.point(lambda x: 0 if x < 180 else 255, "1")

        texto = pytesseract.image_to_string(
            img,
            lang="spa",
            config="--psm 6"
        )

        texto_total += texto + "\n"

    print("✅ OCR completado")
    return texto_total
