# api-dca-ocr/api_routes.py

from flask import Blueprint, jsonify, send_file, abort, Response
from database import SessionLocal
from models import Edicion, Transcripcion, Resumen
import os

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/ediciones', methods=['GET'])
def listar_ediciones():
    session = SessionLocal()
    try:
        ediciones = session.query(Edicion).order_by(Edicion.fecha_publicacion.desc()).all()
        return jsonify([{
            'id': e.id,
            'numero_diario': e.numero_diario,
            'fecha_publicacion': e.fecha_publicacion.isoformat(),
            'estado': e.estado,
        } for e in ediciones])
    finally:
        session.close()


@api_bp.route('/ediciones/<int:edicion_id>', methods=['GET'])
def obtener_edicion(edicion_id):
    session = SessionLocal()
    try:
        e = session.query(Edicion).get(edicion_id)
        if not e:
            abort(404)
        return jsonify({
            'id': e.id,
            'numero_diario': e.numero_diario,
            'fecha_publicacion': e.fecha_publicacion.isoformat(),
            'estado': e.estado,
        })
    finally:
        session.close()


@api_bp.route('/resumenes/<int:edicion_id>', methods=['GET'])
def obtener_resumen(edicion_id):
    session = SessionLocal()
    try:
        r = session.query(Resumen).filter_by(edicion_id=edicion_id).first()
        if not r:
            abort(404)
        return jsonify({
            'id': r.id,
            'edicion_id': r.edicion_id,
            'contenido_html': r.contenido_html if hasattr(r, 'contenido_html') else r.contenido,
        })
    finally:
        session.close()


@api_bp.route('/ediciones/<int:edicion_id>/pdf', methods=['GET'])
def descargar_pdf(edicion_id):
    ruta = f'reportes/edicion_{edicion_id}.pdf'
    if not os.path.exists(ruta):
        abort(404)
    return send_file(ruta, mimetype='application/pdf', as_attachment=True)

@api_bp.route('/dca/<nombre>/pdf-original', methods=['GET'])
def pdf_original(nombre):
    session = SessionLocal()
    try:
        e = session.query(Edicion).filter_by(nombre_archivo=nombre).first()
        if not e or not e.pdf_dca:
            abort(404)
        return Response(e.pdf_dca, mimetype="application/pdf")
    finally:
        session.close()