import requests
from PIL import Image
from io import BytesIO

url = "https://legal.dca.gob.gt/"
r = requests.get(url)

print(r.headers.get("Content-Type"))
print(len(r.content))

img = Image.open(BytesIO(r.content))
img.show()