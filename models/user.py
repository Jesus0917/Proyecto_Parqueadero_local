from app import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(150), unique=True, nullable=False)
    contrasena = db.Column(db.String(150), nullable=False)  # Cambiado a `contrasena`
    nombreUsuario = db.Column(db.String(150), nullable=False)  # Cambiado a `nombreUsuario`

    def __init__(self, usuario, contrasena, nombreUsuario):
        self.usuario = usuario
        self.contrasena = contrasena
        self.nombreUsuario = nombreUsuario
