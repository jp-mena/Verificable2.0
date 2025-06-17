from sga.db.database import execute_query
from sga.utils.validators import ValidationError, safe_int_conversion, validate_email, validate_required_string
import re
from datetime import datetime

class Alumno:
    def __init__(self, nombre, correo, fecha_ingreso):
        self.nombre = validate_required_string(nombre, "nombre")
        self.correo = validate_email(correo)
        self.fecha_ingreso = self._validate_fecha_ingreso(fecha_ingreso)
    
    def _validate_fecha_ingreso(self, fecha):
        """Valida el formato de fecha de ingreso"""
        if not fecha:
            raise ValidationError("Fecha de ingreso es requerida")
        
        # Asegurar que sea string
        fecha_str = str(fecha).strip()
        
        # Validar formato YYYY-MM-DD
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_str):
            raise ValidationError("Fecha de ingreso debe estar en formato YYYY-MM-DD")
        
        try:
            # Verificar que sea una fecha válida
            datetime.strptime(fecha_str, '%Y-%m-%d')
            return fecha_str
        except ValueError:
            raise ValidationError("Fecha de ingreso no es válida")
    @classmethod
    def crear(cls, nombre, correo, fecha_ingreso):
        """Crea un nuevo alumno"""
        try:
            alumno = cls(nombre, correo, fecha_ingreso)
            query = "INSERT INTO alumnos (nombre, correo, fecha_ingreso) VALUES (%s, %s, %s)"
            id_alumno = execute_query(query, (alumno.nombre, alumno.correo, alumno.fecha_ingreso))
            return alumno
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al crear alumno: {str(e)}")
    
    @classmethod
    def obtener_todos(cls):
        """Obtiene todos los alumnos en formato consistente"""
        try:
            query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos ORDER BY nombre"
            return execute_query(query)
        except Exception as e:
            raise ValidationError(f"Error al obtener todos los alumnos: {str(e)}")
    
    def save(self):
        """Guarda un nuevo alumno en la base de datos"""
        try:
            query = "INSERT INTO alumnos (nombre, correo, fecha_ingreso) VALUES (%s, %s, %s)"
            return execute_query(query, (self.nombre, self.correo, self.fecha_ingreso))
        except Exception as e:
            raise ValidationError(f"Error al guardar alumno: {str(e)}")
    
    @staticmethod
    def get_all():
        """Obtiene todos los alumnos"""
        try:
            query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos"
            return execute_query(query)
        except Exception as e:
            raise ValidationError(f"Error al obtener alumnos: {str(e)}")
    
    @staticmethod
    def get_by_id(alumno_id):
        """Obtiene un alumno por su ID"""
        try:
            alumno_id = safe_int_conversion(alumno_id)
            if alumno_id is None or alumno_id <= 0:
                raise ValidationError("ID de alumno debe ser un entero positivo")
            
            query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos WHERE id = %s"
            results = execute_query(query, (alumno_id,))
            return results[0] if results else None
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al obtener alumno por ID: {str(e)}")
    
    @staticmethod
    def update(alumno_id, nombre, correo, fecha_ingreso):
        """Actualiza un alumno existente"""
        try:
            alumno_id = safe_int_conversion(alumno_id)
            if alumno_id is None or alumno_id <= 0:
                raise ValidationError("ID de alumno debe ser un entero positivo")
            
            # Validar datos
            nombre = validate_required_string(nombre, "nombre")
            correo = validate_email(correo)
            
            # Validar fecha
            if not fecha_ingreso:
                raise ValidationError("Fecha de ingreso es requerida")
            fecha_str = str(fecha_ingreso).strip()
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_str):
                raise ValidationError("Fecha de ingreso debe estar en formato YYYY-MM-DD")
            
            query = "UPDATE alumnos SET nombre = %s, correo = %s, fecha_ingreso = %s WHERE id = %s"
            execute_query(query, (nombre, correo, fecha_str, alumno_id))
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al actualizar alumno: {str(e)}")
    
    @staticmethod
    def delete(alumno_id):
        """Elimina un alumno"""
        try:
            alumno_id = safe_int_conversion(alumno_id)
            if alumno_id is None or alumno_id <= 0:
                raise ValidationError("ID de alumno debe ser un entero positivo")
            
            # Verificar si el alumno existe
            existing = Alumno.get_by_id(alumno_id)
            if not existing:
                raise ValidationError("Alumno no encontrado")
            
            query = "DELETE FROM alumnos WHERE id = %s"
            execute_query(query, (alumno_id,))
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al eliminar alumno: {str(e)}")
    
    @classmethod
    def obtener_por_id(cls, alumno_id):
        """Obtiene un alumno por su ID (método de compatibilidad)"""
        result = cls.get_by_id(alumno_id)
        if result:
            return {
                'id': result[0],
                'nombre': result[1], 
                'correo': result[2],
                'fecha_ingreso': result[3]
            }
        return None
    
    @staticmethod
    def get_by_correo(correo):
        """Obtiene un alumno por su correo"""
        query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos WHERE correo = %s"
        results = execute_query(query, (correo,))
        return results[0] if results else None
    
    @staticmethod
    def update(alumno_id, nombre, correo, fecha_ingreso):
        """Actualiza un alumno existente"""
        query = "UPDATE alumnos SET nombre = %s, correo = %s, fecha_ingreso = %s WHERE id = %s"
        return execute_query(query, (nombre, correo, fecha_ingreso, alumno_id))
    
    @staticmethod
    def delete(alumno_id):
        """Elimina un alumno"""
        query = "DELETE FROM alumnos WHERE id = %s"
        return execute_query(query, (alumno_id,))
