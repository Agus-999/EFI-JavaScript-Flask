from datetime import timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import check_password_hash
from models import User
from app import db
from schemas import UserSchemas, NoAdminSchemas
from marshmallow import ValidationError

auth_db = Blueprint('auth', __name__)

@auth_db.route("/login", methods=['POST'])
def login():
    data = request.authorization
    if not data or not data.username or not data.password:
        return jsonify({"Mensaje": "Se requiere nombre de usuario y contraseña"}), 400

    username = data.username
    password = data.password

    usuario = User.query.filter_by(username=username).first()
    
    if usuario and (usuario.password_hash == password or check_password_hash(usuario.password_hash, password)):
        access_token = create_access_token(
            identity=username,
            expires_delta=timedelta(minutes=60),
            additional_claims={"administrador": usuario.is_admin}
        )
        return jsonify({'Token': f'Bearer {access_token}'}), 200

    return jsonify({"Mensaje": "El usuario y la contraseña no coinciden"}), 401

@auth_db.route('/users', methods=['GET', 'POST'])
@jwt_required()
def users():
    additional_data = get_jwt()
    administrador = additional_data.get("administrador")
    
    if request.method == 'POST':
        if administrador:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return jsonify({"mensaje": "Se requieren nombre de usuario y contraseña"}), 400

            # Validar el username usando UserSchemas
            schema = UserSchemas()
            try:
                schema.load({"username": username}, partial=("password_hash", "is_admin"))

                nuevo_usuario = User(
                    username=username,
                    password_hash=password,
                    is_admin=False
                )
                db.session.add(nuevo_usuario)
                db.session.commit()
                return jsonify({
                    "mensaje": "Usuario creado correctamente",
                    "Usuario": {"username": nuevo_usuario.username}
                }), 201
            except ValidationError as e:
                return jsonify({"mensaje": "El nombre de usuario ya existe", "errores": e.messages}), 400

        else:
            return jsonify({"mensaje": "Solo el admin puede crear nuevos usuarios"}), 403

    usuarios = User.query.all()
    if administrador:
        return UserSchemas().dump(obj=usuarios, many=True), 200
    else:
        return NoAdminSchemas().dump(obj=usuarios, many=True), 200

@auth_db.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    additional_data = get_jwt()
    administrador = additional_data.get("administrador")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"mensaje": "El usuario no existe"}), 404

    if administrador:
        user_data = UserSchemas().dump(user)
    else:
        user_data = NoAdminSchemas().dump(user)
    
    return jsonify(user_data), 200

@auth_db.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    additional_data = get_jwt()
    administrador = additional_data.get("administrador")
    
    if not administrador:
        return jsonify({"mensaje": "Solo el administrador puede eliminar usuarios"}), 403

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200
    else:
        return jsonify({"mensaje": "El usuario no existe"}), 404

@auth_db.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def edit_user(user_id):
    additional_data = get_jwt()
    administrador = additional_data.get("administrador")
    
    if not administrador:
        return jsonify({"mensaje": "Solo el administrador puede editar usuarios"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"mensaje": "El usuario no existe"}), 404

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username:
        user.username = username
    if password:
        user.password_hash = password  # Actualiza el hash de la contraseña

    db.session.commit()
    return jsonify({"mensaje": "Usuario editado correctamente"}), 200
