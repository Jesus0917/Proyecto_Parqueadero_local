from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required
from app import db, bcrypt
from models.user import Usuario

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        user = Usuario.query.filter_by(usuario=usuario).first()
        if user and bcrypt.check_password_hash(user.contrasena, password):
            login_user(user)
            session.permanent = True  # Esto usa PERMANENT_SESSION_LIFETIME
            return redirect(url_for('main.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        nombreUsuario = request.form['nombreUsuario']
        admin_usuario = request.form['admin_usuario']
        admin_password = request.form['admin_password']

        if admin_usuario != 'admin':
            flash('Autorización del administrador fallida. Solo el usuario "admin" puede autorizar el registro.', 'danger')
            return redirect(url_for('auth.register'))

        admin_user = Usuario.query.filter_by(usuario=admin_usuario).first()
        if not admin_user or not bcrypt.check_password_hash(admin_user.contrasena, admin_password):
            flash('Autorización del administrador fallida. Credenciales incorrectas.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = Usuario(usuario=usuario, contrasena=hashed_password, nombreUsuario=nombreUsuario)
        db.session.add(new_user)
        db.session.commit()
        flash('Cuenta creada exitosamente, por favor inicie sesión', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
