from app import db
from datetime import datetime

class RegistroFinal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), nullable=False)
    imagen_entrada = db.Column(db.LargeBinary, nullable=False)
    imagen_salida = db.Column(db.LargeBinary, nullable=False)
    fecha_hora_entrada = db.Column(db.DateTime, nullable=False)
    fecha_hora_salida = db.Column(db.DateTime, nullable=False)

    def __init__(self, placa, imagen_entrada, imagen_salida, fecha_hora_entrada, fecha_hora_salida):
        self.placa = placa
        self.imagen_entrada = imagen_entrada
        self.imagen_salida = imagen_salida
        self.fecha_hora_entrada = fecha_hora_entrada
        self.fecha_hora_salida = fecha_hora_salida

    @property
    def tiempo_en_parqueadero(self):
        return self.fecha_hora_salida - self.fecha_hora_entrada