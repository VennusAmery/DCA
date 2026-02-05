from flask import Flask, request, jsonify
from services.dca_scraper import obtener_imagenes_dca
from services.image_downloader import descargar_imagenes
from services.ocr_service import ocr_imagenes

app = Flask(__name__)

@app.route('/')
def home():
    return 'API DCA funcionando'

@app.route('/api/dca/procesar', methods=['GET'])
def procesar_dca():
    url = request.args.get('url')

    if not url:
        return jsonify({'error': 'URL del DCA requerida'}), 400

    try:
        imagenes_url = obtener_imagenes_dca(url)
        imagenes = descargar_imagenes(imagenes_url)
        texto = ocr_imagenes(imagenes)

        return jsonify({
            'mensaje': 'DCA procesado correctamente',
            'paginas': len(imagenes),
            'caracteres': len(texto)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
