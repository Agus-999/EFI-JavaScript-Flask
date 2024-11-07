from .auth_view import auth_db
from .vehiculos_view import vehiculo_db

def register_db(app):
    app.register_blueprint(auth_db)
    app.register_blueprint(vehiculo_db)