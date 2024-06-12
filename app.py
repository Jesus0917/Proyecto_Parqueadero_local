from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, logout_user
from flask_session import Session
import base64


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
sess = Session()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    sess.init_app(app)

    with app.app_context():
        from models import user, placa, registro_final
        db.create_all()

        # Registro del filtro personalizado para base64
        @app.template_filter('b64encode')
        def b64encode_filter(data):
            return base64.b64encode(data).decode('utf-8')

    from views.main import main as main_blueprint
    from views.placa import placa as placa_blueprint
    from views.auth import auth as auth_blueprint
    from views.stats import stats as stats_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(placa_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(stats_blueprint)

    return app

@login_manager.user_loader
def load_user(user_id):
    from models.user import Usuario
    return Usuario.query.get(int(user_id))

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
