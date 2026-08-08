"""
python app.py  

"""
import re
from pathlib import Path
import json

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from services.auto_dca import ejecutar_automatico
from services.control_descargas import cargar_registro

app = Flask(__name__)
CORS(app)

TXT_DIR = Path("storage/textos")
REPORTES_DIR = Path("storage/reportes")
RESUMENES_DIR = Path("storage/resumenes")
MAPA_PATH = Path("storage/mapa.json")

scheduler = BackgroundScheduler(timezone="America/Guatemala")
scheduler.add_job(
    ejecutar_automatico,
    trigger=CronTrigger(hour=10, minute=0, timezone="America/Guatemala"),
    id="dca_diario",
    replace_existing=True,
)
scheduler.start()


def _cargar_procesados():
    data = cargar_registro()
    return data.get("procesados", [])


def _cargar_mapa():
    if not MAPA_PATH.exists():
        return {}
    try:
        return json.loads(MAPA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _md_a_html(md: str) -> str:
    """Conversión simple de markdown a HTML (headers ## y negritas **)."""
    html = []
    for linea in md.split("\n"):
        linea = linea.strip()
        if not linea:
            continue
        if linea.startswith("### "):
            html.append(f"<h4>{linea[4:]}</h4>")
        elif linea.startswith("## "):
            html.append(f"<h3>{linea[3:]}</h3>")
        else:
            linea = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", linea)
            html.append(f"<p>{linea}</p>")
    return "\n".join(html)


@app.route('/')
def home():
    return 'API DCA funcionando'


@app.route('/api/dca/procesar', methods=['GET'])
def procesar_dca():
    try:
        ejecutar_automatico()
        return jsonify({'mensaje': 'Proceso ejecutado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ediciones', methods=['GET'])
def listar_ediciones():
    procesados = _cargar_procesados()
    mapa = _cargar_mapa()
    resultado = []
    for nombre in procesados:
        base = Path(nombre).stem
        entrada = mapa.get(base)
        estado = 'resumido' if entrada else 'transcrito'

        tema = nombre
        temas_secundarios = []
        if entrada and entrada.get("resumen"):
            ruta_resumen = RESUMENES_DIR / entrada["resumen"]
            if ruta_resumen.exists() and ruta_resumen.is_file():
                lineas = ruta_resumen.read_text(encoding="utf-8").split("\n")
                for linea in lineas:
                    linea = linea.strip()
                    if linea.startswith("# ") and tema == nombre:
                        tema = linea[2:].strip()
                    elif linea.startswith("## "):
                        temas_secundarios.append(linea[3:].strip())
                    if len(temas_secundarios) >= 3:
                        break

        resultado.append({
            'nombre': nombre,
            'estado': estado,
            'tema': tema,
            'temas_secundarios': temas_secundarios,
        })
    return jsonify(resultado)

@app.route('/api/ediciones/<path:nombre>', methods=['GET'])
def obtener_edicion(nombre):
    procesados = _cargar_procesados()
    if nombre not in procesados:
        return jsonify({'error': 'No encontrado'}), 404

    base = Path(nombre).stem
    mapa = _cargar_mapa()
    entrada = mapa.get(base)

    texto = ""
    ruta_txt = TXT_DIR / f"{base}.txt"
    if ruta_txt.exists():
        texto = ruta_txt.read_text(encoding="utf-8")

    resumen_html = ""
    tiene_pdf_reporte = False
    if entrada:
        ruta_resumen = RESUMENES_DIR / entrada["resumen"]
        if ruta_resumen.exists():
            resumen_html = _md_a_html(ruta_resumen.read_text(encoding="utf-8"))
        tiene_pdf_reporte = (REPORTES_DIR / entrada["reporte"]).exists()

    return jsonify({
        'nombre': nombre,
        'texto': texto,
        'resumen_html': resumen_html,
        'tiene_pdf_reporte': tiene_pdf_reporte,
    })


@app.route('/api/ediciones/<path:nombre>/pdf', methods=['GET'])
def descargar_pdf(nombre):
    base = Path(nombre).stem
    mapa = _cargar_mapa()
    entrada = mapa.get(base)
    if not entrada:
        return jsonify({'error': 'Reporte no generado aún'}), 404

    ruta = REPORTES_DIR / entrada["reporte"]
    if not ruta.exists():
        return jsonify({'error': 'Reporte no generado aún'}), 404

    return send_file(str(ruta), mimetype='application/pdf')


if __name__ == '__main__':
    app.run(debug=True, port=5002)
