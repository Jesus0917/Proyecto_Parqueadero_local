from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from models.placa import Placa

main = Blueprint('main', __name__)

# Definir la capacidad máxima del parqueadero
CAPACIDAD_MAXIMA_PARQUEADERO = 15

@main.route('/')
@login_required
def index():
    placas_count = Placa.query.count()
    espacios_disponibles = CAPACIDAD_MAXIMA_PARQUEADERO - placas_count
    return render_template('index.html', placas_count=placas_count, espacios_disponibles=espacios_disponibles)

@main.route('/placas_count')
@login_required
def placas_count():
    count = Placa.query.count()
    available_spaces = CAPACIDAD_MAXIMA_PARQUEADERO - count
    return jsonify(count=count, available_spaces=available_spaces)
