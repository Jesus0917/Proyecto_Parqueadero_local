from app import db

class Placa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), nullable=False)
    imagen = db.Column(db.LargeBinary, nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)

    def __init__(self, placa, imagen, fecha_hora):
        self.placa = placa
        self.imagen = imagen
        self.fecha_hora = fecha_hora
