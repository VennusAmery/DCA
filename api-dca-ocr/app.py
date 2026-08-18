"""
python app.py
"""
from io import BytesIO

from flask import Flask, jsonify, send_file, abort
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from services.auto_dca import ejecutar_automatico
from database import SessionLocal
from database.models import Edicion, Resumen

app = Flask(__name__)
CORS(app, origins=["https://dca-three.vercel.app"])

scheduler = BackgroundScheduler(timezone="America/Guatemala")
scheduler.add_job(
    ejecutar_automatico,
    trigger=CronTrigger(hour=10, minute=0, timezone="America/Guatemala"),
    id="dca_diario",
    replace_existing=True,
)
scheduler.start()


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
    db = SessionLocal()
    try:
        ediciones = db.query(Edicion).order_by(Edicion.fecha_publicacion.desc()).all()
        return jsonify([{
            'nombre': e.nombre_archivo,
            'fecha_publicacion': e.fecha_publicacion.isoformat() if e.fecha_publicacion else None,
            'estado': e.estado,
        } for e in ediciones])
    finally:
        db.close()


@app.route('/api/ediciones/<path:nombre>', methods=['GET'])
def obtener_edicion(nombre):
    db = SessionLocal()
    try:
        e = db.query(Edicion).filter_by(nombre_archivo=nombre).first()
        if not e:
            abort(404)

        texto = e.transcripcion.texto if e.transcripcion else ""
        resumen_html = e.resumen.contenido_html if e.resumen and e.resumen.contenido_html else ""
        tiene_pdf_reporte = bool(e.resumen and e.resumen.reporte_pdf)

        return jsonify({
            'nombre': e.nombre_archivo,
            'fecha_publicacion': e.fecha_publicacion.isoformat() if e.fecha_publicacion else None,
            'estado': e.estado,
            'texto': texto,
            'resumen_html': resumen_html,
            'tiene_pdf_reporte': tiene_pdf_reporte,
        })
    finally:
        db.close()


@app.route('/api/ediciones/<path:nombre>/pdf', methods=['GET'])
def descargar_pdf(nombre):
    db = SessionLocal()
    try:
        e = db.query(Edicion).filter_by(nombre_archivo=nombre).first()
        if not e or not e.resumen or not e.resumen.reporte_pdf:
            return jsonify({'error': 'Reporte no generado aún'}), 404

        return send_file(
            BytesIO(e.resumen.reporte_pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=e.resumen.reporte_nombre or f'{nombre}.pdf',
        )
    finally:
        db.close()


if __name__ == '__main__':
    app.run(debug=True, port=5002)