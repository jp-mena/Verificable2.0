from sga.db.database import execute_query
from sga.utils.validators import ValidationError, safe_int_conversion, validate_email, validate_required_string

class Profesor:
    def __init__(self, nombre, correo):
        self.nombre = validate_required_string(nombre, "nombre")
        self.correo = validate_email(correo)
    
    def save(self):
        """Guarda un nuevo profesor en la base de datos"""
        try:
            query = "INSERT INTO profesores (nombre, correo) VALUES (?, ?)"
            return execute_query(query, (self.nombre, self.correo))
        except Exception as e:
            raise ValidationError(f"Error al guardar profesor: {str(e)}")
    
    @staticmethod
    def get_all():
        """Obtiene todos los profesores"""
        try:
            query = "SELECT id, nombre, correo FROM profesores"
            return execute_query(query)
        except Exception as e:
            raise ValidationError(f"Error al obtener profesores: {str(e)}")
    
    @classmethod
    def obtener_todos(cls):
        """Obtiene todos los profesores (método de compatibilidad)"""
        return cls.get_all()
    
    @classmethod
    def crear(cls, nombre, correo):
        """Crea un nuevo profesor (método de compatibilidad)"""
        try:
            profesor = cls(nombre, correo)
            profesor_id = profesor.save()
            return profesor
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al crear profesor: {str(e)}")
    
    @staticmethod
    def get_by_id(profesor_id):
        """Obtiene un profesor por su ID"""
        try:
            profesor_id = safe_int_conversion(profesor_id)
            if profesor_id is None or profesor_id <= 0:
                raise ValidationError("ID de profesor debe ser un entero positivo")
            
            query = "SELECT id, nombre, correo FROM profesores WHERE id = ?"
            results = execute_query(query, (profesor_id,))
            return results[0] if results else None
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al obtener profesor por ID: {str(e)}")
    
    @staticmethod
    def get_by_correo(correo):
        """Obtiene un profesor por su correo"""
        try:
            correo = validate_email(correo)
            query = "SELECT id, nombre, correo FROM profesores WHERE correo = ?"
            results = execute_query(query, (correo,))
            return results[0] if results else None
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al obtener profesor por correo: {str(e)}")
    
    @staticmethod
    def update(profesor_id, nombre, correo):
        """Actualiza un profesor existente"""
        try:
            profesor_id = safe_int_conversion(profesor_id)
            if profesor_id is None or profesor_id <= 0:
                raise ValidationError("ID de profesor debe ser un entero positivo")
            
            # Validar datos
            nombre = validate_required_string(nombre, "nombre")
            correo = validate_email(correo)
            
            query = "UPDATE profesores SET nombre = ?, correo = ? WHERE id = ?"
            execute_query(query, (nombre, correo, profesor_id))
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al actualizar profesor: {str(e)}")
    
    @staticmethod
    def delete(profesor_id):
        """Elimina un profesor"""
        try:
            profesor_id = safe_int_conversion(profesor_id)
            if profesor_id is None or profesor_id <= 0:
                raise ValidationError("ID de profesor debe ser un entero positivo")
            
            # Verificar si el profesor existe
            existing = Profesor.get_by_id(profesor_id)
            if not existing:
                raise ValidationError("Profesor no encontrado")
            
            query = "DELETE FROM profesores WHERE id = ?"
            execute_query(query, (profesor_id,))
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al eliminar profesor: {str(e)}")
    
    @staticmethod
    def delete(profesor_id):
        """Elimina un profesor"""
        query = "DELETE FROM profesores WHERE id = ?"
        return execute_query(query, (profesor_id,))
