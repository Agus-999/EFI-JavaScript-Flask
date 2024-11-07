from flask import Blueprint, request, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app import db

from models import Vehiculo, Tipo, Marca, User
from schemas import VehiculosSchemas, TipoSchemas, MarcaSchemas


vehiculo_db = Blueprint('vehiculos', __name__)

# Ruta para obtener todas las marcas
@vehiculo_db.route('/marcas', methods=['GET', 'POST'])
def marcas():
    if request.method == 'GET':
        # Obtener todas las marcas con id y nombre
        marcas = Marca.query.all()
        return jsonify([{'id': marca.id, 'nombre': marca.nombre} for marca in marcas])

    elif request.method == 'POST':
        # Crear una nueva marca
        data = request.get_json()  # O usar request.form si envías datos como formulario
        nombre = data.get('nombre')  # Obtener el campo 'nombre' del cuerpo del POST
        
        if not nombre:
            return jsonify({'error': 'El nombre de la marca es obligatorio'}), 400

        nueva_marca = Marca(nombre=nombre)
        db.session.add(nueva_marca)
        db.session.commit()
        
        return jsonify({'marca creada': nueva_marca.nombre}), 201

@vehiculo_db.route('/marcas/<int:id>', methods=['PUT', 'DELETE'])
def editar_o_eliminar_marca(id):
    # Buscar la marca por su id
    marca = Marca.query.get(id)
    
    if not marca:
        return jsonify({'error': 'Marca no encontrada'}), 404

    if request.method == 'PUT':
        # Editar la marca
        data = request.get_json()
        nombre = data.get('nombre')

        if not nombre:
            return jsonify({'error': 'El nombre de la marca es obligatorio'}), 400

        marca.nombre = nombre
        db.session.commit()
        
        return jsonify({'marca actualizada': {'id': marca.id, 'nombre': marca.nombre}}), 200

    elif request.method == 'DELETE':
        # Eliminar la marca
        db.session.delete(marca)
        db.session.commit()
        
        return jsonify({'marca eliminada': marca.nombre}), 200


# Ruta para obtener todos los tipos
@vehiculo_db.route('/tipos', methods=['GET', 'POST'])
def tipos():
    if request.method == 'GET':
        # Obtener todos los tipos
        tipos = Tipo.query.all()
        # Retornar una lista con los id y nombres de los tipos
        return jsonify([{'id': tipo.id, 'nombre': tipo.nombre} for tipo in tipos])

    elif request.method == 'POST':
        # Crear un nuevo tipo
        data = request.get_json()
        nombre = data.get('nombre')

        if not nombre:
            return jsonify({'error': 'El nombre del tipo es obligatorio'}), 400

        nuevo_tipo = Tipo(nombre=nombre)
        db.session.add(nuevo_tipo)
        db.session.commit()

        return jsonify({'tipo creado': {'id': nuevo_tipo.id, 'nombre': nuevo_tipo.nombre}}), 201
@vehiculo_db.route('/tipos/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def editar_o_eliminar_tipo(id):
    # Buscar el tipo por su id
    tipo = Tipo.query.get(id)
    
    if not tipo:
        return jsonify({'error': 'Tipo no encontrado'}), 404

    if request.method == 'GET':
        # Retornar el tipo como JSON
        return jsonify({'id': tipo.id, 'nombre': tipo.nombre}), 200

    if request.method == 'PUT':
        # Editar el tipo
        data = request.get_json()
        nombre = data.get('nombre')

        if not nombre:
            return jsonify({'error': 'El nombre del tipo es obligatorio'}), 400

        tipo.nombre = nombre
        db.session.commit()
        
        return jsonify({'tipo actualizado': {'id': tipo.id, 'nombre': tipo.nombre}}), 200

    elif request.method == 'DELETE':
        # Eliminar el tipo
        db.session.delete(tipo)
        db.session.commit()
        
        return jsonify({'tipo eliminado': tipo.nombre}), 200


# Ruta para obtener todos los vehículos o crear un nuevo vehículo
@vehiculo_db.route('/vehiculos', methods=['GET', 'POST'])
@jwt_required()
def vehiculos():
    additional_data = get_jwt()
    administrador = additional_data.get("administrador")

    if request.method == 'POST':
        if administrador:
            data = request.get_json()
            schema = VehiculosSchemas()
            errors = schema.validate(data)
            if errors:
                return make_response(jsonify({"error": "Datos inválidos", "detalles": errors}), 400)
            
            nuevo_vehiculo = Vehiculo(
                modelo=data.get('modelo'),
                anio_fabricacion=data.get('anio_fabricacion'),
                precio=data.get('precio'),
                marca_id=data.get('marca_id'),
                tipo_id=data.get('tipo_id')
            )
            db.session.add(nuevo_vehiculo)
            db.session.commit()
            return VehiculosSchemas().dump(nuevo_vehiculo), 201
        else:
            return jsonify({"Mensaje": "Solo el admin puede crear vehículos nuevos"}), 403

    # GET: Obtener todos los vehículos
    vehiculos = Vehiculo.query.all()
    return VehiculosSchemas().dump(vehiculos, many=True), 200

@vehiculo_db.route('/vehiculos/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def modificar_o_eliminar_vehiculo(id):
    additional_data = get_jwt()
    administrador = additional_data.get("administrador")

    # Verificar si el usuario es administrador
    if not administrador:
        return jsonify({"Mensaje": "Solo el admin puede modificar o eliminar vehículos"}), 403

    # Buscar el vehículo por ID
    vehiculo = Vehiculo.query.get(id)  # Utiliza get() en lugar de get_or_404()
    
    if not vehiculo:
        return jsonify({"Mensaje": "Vehículo no encontrado"}), 404

    if request.method == 'PUT':
        # Actualizar un vehículo existente
        data = request.get_json()
        schema = VehiculosSchemas()
        errors = schema.validate(data)
        
        # Validación de los datos
        if errors:
            return make_response(jsonify({"error": "Datos inválidos", "detalles": errors}), 400)

        # Actualizar los campos del vehículo
        vehiculo.modelo = data.get('modelo', vehiculo.modelo)
        vehiculo.anio_fabricacion = data.get('anio_fabricacion', vehiculo.anio_fabricacion)
        vehiculo.precio = data.get('precio', vehiculo.precio)
        vehiculo.marca_id = data.get('marca_id', vehiculo.marca_id)
        vehiculo.tipo_id = data.get('tipo_id', vehiculo.tipo_id)
        
        db.session.commit()

        # Retornar el vehículo actualizado
        return VehiculosSchemas().dump(vehiculo), 200

    elif request.method == 'DELETE':
        # Eliminar un vehículo
        db.session.delete(vehiculo)
        db.session.commit()

        return jsonify({"Mensaje": "Vehículo eliminado exitosamente"}), 200



@vehiculo_db.route('/marcas/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def obtener_editar_o_eliminar_marca(id):
    # Buscar la marca por su id
    marca = Marca.query.get(id)
    
    if not marca:
        return jsonify({'error': 'Marca no encontrada'}), 404

    if request.method == 'GET':
        # Retornar la marca como JSON
        return jsonify({'id': marca.id, 'nombre': marca.nombre}), 200

    if request.method == 'PUT':
        # Editar la marca
        data = request.get_json()
        nombre = data.get('nombre')

        if not nombre:
            return jsonify({'error': 'El nombre de la marca es obligatorio'}), 400

        marca.nombre = nombre
        db.session.commit()
        
        return jsonify({'marca actualizada': {'id': marca.id, 'nombre': marca.nombre}}), 200

    elif request.method == 'DELETE':
        # Eliminar la marca
        db.session.delete(marca)
        db.session.commit()
        
        return jsonify({'marca eliminada': marca.nombre}), 200