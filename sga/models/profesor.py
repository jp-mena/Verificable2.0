from sga.db.database import execute_query
from sga.utils.validators import ValidationError, safe_int_conversion, validate_email, validate_required_string

class Profesor:      
    def __init__(self, nombre, correo):
        self.nombre = validate_required_string(nombre, "nombre", 100)  # Máximo 100 caracteres
        self.correo = validate_email(correo)
    
    def save(self):
        try:
            if len(self.correo) > 100:
                raise ValidationError("El email no puede exceder 100 caracteres")
            existing_profesor = self.get_by_correo(self.correo)
            if existing_profesor:
                raise ValidationError(f"Ya existe un profesor con el email {self.correo}")
            
            query = "INSERT INTO profesores (nombre, correo) VALUES (%s, %s)"
            return execute_query(query, (self.nombre, self.correo))
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al guardar profesor: {str(e)}")
    
    @staticmethod
    def get_all():
        try:
            query = "SELECT id, nombre, correo FROM profesores"
            return execute_query(query)
        except Exception as e:
            raise ValidationError(f"Error al obtener profesores: {str(e)}")
    
    @classmethod
    def obtener_todos(cls):
        return cls.get_all()
    
    @classmethod
    def crear(cls, nombre, correo):
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
        try:
            profesor_id = safe_int_conversion(profesor_id)
            if profesor_id is None or profesor_id <= 0:
                raise ValidationError("ID de profesor debe ser un entero positivo")
            
            query = "SELECT id, nombre, correo FROM profesores WHERE id = %s"
            results = execute_query(query, (profesor_id,))
            return results[0] if results else None
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al obtener profesor por ID: {str(e)}")
    
    @staticmethod
    def get_by_correo(correo):
        try:
            correo = validate_email(correo)
            query = "SELECT id, nombre, correo FROM profesores WHERE correo = %s"
            results = execute_query(query, (correo,))
            return results[0] if results else None
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al obtener profesor por correo: {str(e)}")
    
    @classmethod
    def obtener_por_correo(cls, correo):
        try:
            query = "SELECT id, nombre, correo FROM profesores WHERE correo = %s"
            resultado = execute_query(query, (correo,))
            if resultado:
                fila = resultado[0]
                profesor = cls(fila[1], fila[2])
                profesor.id = fila[0]
                return profesor
            return None
        except Exception as e:
            print(f"Error obteniendo profesor por correo: {e}")
            return None
    
    @staticmethod
    def update(profesor_id, nombre, correo):
        try:
            profesor_id = safe_int_conversion(profesor_id)
            if profesor_id is None or profesor_id <= 0:
                raise ValidationError("ID de profesor debe ser un entero positivo")
            
            nombre = validate_required_string(nombre, "nombre")
            correo = validate_email(correo)
            
            query = "UPDATE profesores SET nombre = %s, correo = %s WHERE id = %s"
            execute_query(query, (nombre, correo, profesor_id))
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al actualizar profesor: {str(e)}")
    
    @staticmethod
    def delete(profesor_id):
        try:
            profesor_id = safe_int_conversion(profesor_id)
            if profesor_id is None or profesor_id <= 0:
                raise ValidationError("ID de profesor debe ser un entero positivo")
            
            existing = Profesor.get_by_id(profesor_id)
            if not existing:
                raise ValidationError("Profesor no encontrado")
            
            query = "DELETE FROM profesores WHERE id = %s"
            execute_query(query, (profesor_id,))
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al eliminar profesor: {str(e)}")
    
    @staticmethod
    def delete(profesor_id):
        query = "DELETE FROM profesores WHERE id = %s"
        return execute_query(query, (profesor_id,))
