# views/stats.py

from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from models.placa import Placa
from models.registro_final import RegistroFinal
from datetime import datetime, timedelta

stats = Blueprint('stats', __name__)

@stats.route('/estadisticas')
@login_required
def estadisticas():
    total_placas = Placa.query.count()
    total_registros = RegistroFinal.query.count()
    
    today = datetime.today()
    last_week = today - timedelta(days=7)
    registros_semanales = RegistroFinal.query.filter(RegistroFinal.fecha_hora_salida >= last_week).all()
    
    registros_por_dia = {}
    for i in range(7):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        registros_por_dia[day] = 0

    for registro in registros_semanales:
        day = registro.fecha_hora_salida.strftime("%Y-%m-%d")
        if day in registros_por_dia:
            registros_por_dia[day] += 1

    return render_template('stats.html', total_placas=total_placas, total_registros=total_registros, registros_por_dia=registros_por_dia)
