# views/placa.py

from flask import Blueprint, Response, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required
import cv2
import easyocr
import re
from datetime import datetime
from app import db
from models.placa import Placa
from models.registro_final import RegistroFinal
from sqlalchemy.exc import SQLAlchemyError

placa = Blueprint('placa', __name__)

def detectar_placa_en_fotograma(frame, reader, patron_placa):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resultados = reader.readtext(gray)
    placas = []
    for resultado in resultados:
        bbox, texto, confianza = resultado
        (x_min, y_min), (x_max, y_max) = bbox[0], bbox[2]
        altura_texto = y_max - y_min
        if patron_placa.match(texto.replace(" ", "")) and altura_texto > 15:
            placas.append((texto, bbox))
    return placas

def gen():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()

@placa.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@placa.route('/capture', methods=['POST'])
@login_required
def capture():
    reader = easyocr.Reader(['en'])
    patron_placa = re.compile(r'^[A-Z]{3}-?\d{3}$|^[A-Z]{3}-?\d{2}[A-Z]$|^[A-Z]{3}-?\d{2}$')

    def capture_frame():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None, 'Error al acceder a la cámara'
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return None, 'Error al capturar el fotograma'
        return frame, None

    frame, error = capture_frame()
    if error:
        return jsonify({'success': False, 'message': error})

    placas = detectar_placa_en_fotograma(frame, reader, patron_placa)

    if placas:
        placa_texto, bbox = placas[0]
        (x_min, y_min), (x_max, y_max) = bbox[0], bbox[2]
        cv2.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
        _, buffer = cv2.imencode('.jpg', frame)
        imagen = buffer.tobytes()
        fecha_hora = datetime.now()

        try:
            # Verificar si la placa ya está registrada para la entrada
            entrada = Placa.query.filter_by(placa=placa_texto).first()
            if entrada:
                # Mover el registro de entrada a la tabla de registro_final
                nueva_salida = RegistroFinal(
                    placa=placa_texto,
                    imagen_entrada=entrada.imagen,
                    imagen_salida=imagen,
                    fecha_hora_entrada=entrada.fecha_hora,
                    fecha_hora_salida=fecha_hora
                )
                db.session.add(nueva_salida)
                db.session.delete(entrada)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Salida registrada', 'placa': placa_texto})
            else:
                # Registrar nueva entrada
                total_placas = Placa.query.count()
                capacidad_maxima = 15
                if total_placas >= capacidad_maxima:
                    return jsonify({'success': False, 'message': 'Capacidad máxima alcanzada, no se puede registrar la entrada'})
                
                nueva_placa = Placa(placa=placa_texto, imagen=imagen, fecha_hora=fecha_hora)
                db.session.add(nueva_placa)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Entrada registrada', 'placa': placa_texto})
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Error al guardar en la base de datos', 'error': str(e)})
    else:
        return jsonify({'success': False, 'message': 'No se detectaron placas'})

@placa.route('/placas')
@login_required
def mostrar_placas():
    placas = Placa.query.all()
    return render_template('placas.html', placas=placas)

@placa.route('/registro_final', methods=['GET', 'POST'])
@login_required
def mostrar_registro_final():
    query = ""
    fecha_salida = None

    if request.method == 'POST':
        query = request.form.get('placa', "")
        fecha_salida = request.form.get('fecha_salida', None)

        registros = RegistroFinal.query

        if query:
            registros = registros.filter(RegistroFinal.placa.like(f"%{query}%"))
        if fecha_salida:
            registros = registros.filter(db.func.date(RegistroFinal.fecha_hora_salida) == fecha_salida)

        registros = registros.all()
    else:
        registros = RegistroFinal.query.all()

    return render_template('registro_final.html', registros=registros, query=query)

@placa.route('/placa/delete/<int:id>', methods=['POST'])
@login_required
def eliminar_placa(id):
    placa = Placa.query.get_or_404(id)
    db.session.delete(placa)
    db.session.commit()
    return redirect(url_for('placa.mostrar_placas'))

@placa.route('/placa/edit/<int:id>', methods=['POST'])
@login_required
def editar_placa(id):
    placa = Placa.query.get_or_404(id)
    nuevo_texto = request.form['placa']
    placa.placa = nuevo_texto
    db.session.commit()
    return redirect(url_for('placa.mostrar_placas'))

@placa.route('/buscar', methods=['GET', 'POST'])
@login_required
def buscar_placa():
    if request.method == 'POST':
        query = request.form.get('query')
        resultados = Placa.query.filter(Placa.placa.like(f"%{query}%")).all()
        if resultados:
            return render_template('placas.html', placas=resultados, query=query)
        else:
            flash('No se encontraron resultados')
            return redirect(url_for('placa.mostrar_placas'))
    return redirect(url_for('placa.mostrar_placas'))
