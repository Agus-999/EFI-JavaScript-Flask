import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_restx import Api, Resource
from flask_cors import CORS  # Importar CORS

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Habilitar CORS para la aplicación
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)  # Esto habilita CORS para todas las rutas

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
ma = Marshmallow(app)

api = Api(app, version='1.0', title='API de Ejemplo',
          description='Documentación de la API para gestionar usuarios y vehículos')

from models import User
from View import register_db
register_db(app)

@api.route('/usuarios')
class UsuarioResource(Resource):
    @api.doc('obtener_usuarios')
    def get(self):
        """Obtiene una lista de usuarios"""
        # Lógica para obtener usuarios
        return {'usuarios': []}

    @api.doc('crear_usuario')
    def post(self):
        """Crea un nuevo usuario"""
        # Lógica para crear un usuario
        return {'mensaje': 'Usuario creado'}

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # Para usar HTTPS de forma temporal en desarrollo
