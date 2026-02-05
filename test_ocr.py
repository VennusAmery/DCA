from PIL import Image
from services.ocr_service import ocr_imagenes

img = Image.open("storage/images/page_1.png")
print("Imagen cargada:", img.size, img.mode)

texto = ocr_imagenes([img])
print("=== TEXTO OCR ===")
print(texto)
