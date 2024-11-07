from app import ma, db
from models import User, Tipo, Marca, Vehiculo
from marshmallow import validates, ValidationError, fields
from datetime import datetime

# Esquema para los usuarios
class UserSchemas(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ("id", "username", "password_hash", "is_admin")

    # Validación del nombre de usuario para verificar si ya existe
    @validates("username")
    def validate_username(self, value):
        if User.query.filter_by(username=value).first():
            raise ValidationError("El nombre de usuario ya existe")
    
    # Validación para verificar si el usuario existe antes de editar o eliminar
    @validates("id")
    def validate_user_exists(self, user_id):
        user = User.query.get(user_id)
        if user is None:
            raise ValidationError("El usuario no existe")

# Esquema sin administrador (solo nombre de usuario)
class NoAdminSchemas(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ("username",)

# Esquema para el tipo de vehículo
class TipoSchemas(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tipo
        fields = ("id", "nombre",)

# Esquema para la marca de vehículos
class MarcaSchemas(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Marca
        fields = ("id", "nombre",)

# Esquema para los vehículos
class VehiculosSchemas(ma.SQLAlchemyAutoSchema):
    marca = fields.Nested(MarcaSchemas, only=("id", "nombre"))
    tipo = fields.Nested(TipoSchemas, only=("id", "nombre"))
    
    class Meta:
        model = Vehiculo
        fields = ("id", "modelo", "anio_fabricacion", "precio", "marca_id", "tipo_id")

    # Validación para el año de fabricación
    @validates('anio_fabricacion')
    def validate_anio_fabricacion(self, value):
        current_year = datetime.now().year
        if value < current_year:
            raise ValidationError("El año de fabricación debe ser el año actual o posterior.")
    
    # Validación para el precio, asegurando que sea mayor que 0
    @validates('precio')
    def validate_precio(self, value):
        if value <= 0:
            raise ValidationError("El precio debe ser un valor positivo.")
    
    # Validación para la existencia de la marca en la base de datos
    @validates('marca_id')
    def validate_marca_id(self, value):
        marca = Marca.query.get(value)
        if marca is None:
            raise ValidationError("La marca con ese ID no existe.")
    
    # Validación para la existencia del tipo en la base de datos
    @validates('tipo_id')
    def validate_tipo_id(self, value):
        tipo = Tipo.query.get(value)
        if tipo is None:
            raise ValidationError("El tipo con ese ID no existe.")
    
    # Validación para el modelo, asegurándose que no sea vacío
    @validates('modelo')
    def validate_modelo(self, value):
        if not value:
            raise ValidationError("El modelo no puede estar vacío.")
    
    # Validación para asegurar que el año de fabricación es un número entero
    @validates('anio_fabricacion')
    def validate_anio_fabricacion_type(self, value):
        if not isinstance(value, int):
            raise ValidationError("El año de fabricación debe ser un número entero.")
    
    # Validación para asegurarse de que los campos ID son enteros
    @validates('marca_id')
    def validate_marca_id_type(self, value):
        if not isinstance(value, int):
            raise ValidationError("El ID de la marca debe ser un número entero.")
    
    @validates('tipo_id')
    def validate_tipo_id_type(self, value):
        if not isinstance(value, int):
            raise ValidationError("El ID del tipo debe ser un número entero.")
