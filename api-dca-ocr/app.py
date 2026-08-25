"""
python app.py
"""
from io import BytesIO

from flask import Flask, jsonify, send_file, abort
from flask_cors import CORS
from flask import redirect
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from services.auto_dca import ejecutar_automatico
from database import SessionLocal
from database.models import Edicion, Resumen

from b2sdk.v2 import InMemoryAccountInfo, B2Api
import os

app = Flask(__name__)
CORS(app, origins=["https://dca-three.vercel.app"])

info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", os.getenv("B2_KEY_ID"), os.getenv("B2_APP_KEY"))
bucket = b2_api.get_bucket_by_name(os.getenv("B2_BUCKET_NAME"))

scheduler = BackgroundScheduler(timezone="America/Guatemala")
scheduler.add_job(
    ejecutar_automatico,
    trigger=CronTrigger(hour=10, minute=0, timezone="America/Guatemala"),
    id="dca_diario",
    replace_existing=True,
)
scheduler.start()

def buscar_edicion(db, nombre):
    nombre_sin_ext = nombre[:-4] if nombre.endswith('.pdf') else nombre
    nombre_con_ext = f"{nombre_sin_ext}.pdf"
    
    return db.query(Edicion).filter(
        (Edicion.nombre_archivo == nombre) |
        (Edicion.nombre_archivo == nombre_sin_ext) |
        (Edicion.nombre_archivo == nombre_con_ext)
    ).first()

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
            'url_pdf_dca': e.url_pdf_dca,
        })
    finally:
        db.close()

@app.route('/api/ediciones/<path:nombre>/pdf-dca', methods=['GET'])
def descargar_pdf_dca(nombre):
    db = SessionLocal()
    try:
        e = buscar_edicion(db, nombre)
        if not e or not e.url_pdf_dca:
            return jsonify({'error': 'PDF original del DCA no disponible'}), 404

        nombre_archivo_b2 = f"dca/{e.nombre_archivo}"
        auth_token = bucket.get_download_authorization(
            file_name_prefix=nombre_archivo_b2,
            valid_duration_in_seconds=3600
        )
        url_firmada = f"{bucket.get_download_url(nombre_archivo_b2)}?Authorization={auth_token}"

        return redirect(url_firmada)
    finally:
        db.close()

@app.route('/api/ediciones/<path:nombre>/pdf', methods=['GET'])
def descargar_pdf_reporte(nombre):
    db = SessionLocal()
    try:
        e = buscar_edicion(db, nombre)
        if not e or not e.resumen or not e.resumen.reporte_pdf:
            return jsonify({'error': 'Reporte PDF no encontrado'}), 404

        return send_file(
            BytesIO(e.resumen.reporte_pdf),
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f"reporte_{e.nombre_archivo}"
        )
    finally:
        db.close()

@app.route('/api/ediciones', methods=['GET'])
def listar_ediciones():
    db = SessionLocal()
    try:
        ediciones = db.query(
            Edicion.nombre_archivo,
            Edicion.fecha_publicacion,
            Edicion.estado
        ).order_by(Edicion.fecha_publicacion.desc()).all()

        return jsonify([{
            'nombre': e.nombre_archivo,
            'fecha_publicacion': e.fecha_publicacion.isoformat() if e.fecha_publicacion else None,
            'estado': e.estado,
        } for e in ediciones])
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True, port=5002)