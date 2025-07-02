from sga.db.database import execute_query
from sga.utils.validators import ValidationError, parse_integer_field, validate_email, validate_required_string
import re
from datetime import datetime

class Alumno:    
    def __init__(self, nombre, correo, fecha_ingreso):
        if len(nombre) > 100:
            raise ValidationError("El nombre no puede exceder 100 caracteres")
        
        if len(correo) > 100:
            raise ValidationError("El email no puede exceder 100 caracteres")
            
        self.nombre = validate_required_string(nombre, "nombre")
        self.correo = validate_email(correo)
        self.fecha_ingreso = self._validate_fecha_ingreso(fecha_ingreso)
        
    def _validate_fecha_ingreso(self, fecha):
        if not fecha:
            raise ValidationError("Fecha de ingreso es requerida")
        
        fecha_str = str(fecha).strip()
        
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_str):
            raise ValidationError("Fecha de ingreso debe estar en formato YYYY-MM-DD")
        
        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
            
            if fecha_obj.year < 1950:
                raise ValidationError("La fecha de ingreso no puede ser anterior a 1950")
                
            if fecha_obj > datetime.now():
                raise ValidationError("La fecha de ingreso no puede ser futura")
                
            return fecha_str
        except ValueError:
            raise ValidationError("Fecha de ingreso no es válida")
        
    @classmethod
    def crear(cls, nombre, correo, fecha_ingreso):
        try:
            alumno = cls(nombre, correo, fecha_ingreso)
            query = "INSERT INTO alumnos (nombre, correo, fecha_ingreso) VALUES (%s, %s, %s)"
            execute_query(query, (alumno.nombre, alumno.correo, alumno.fecha_ingreso))
            return alumno
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al crear alumno: {str(e)}")
    
    @classmethod
    def obtener_todos(cls):
        try:
            query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos ORDER BY nombre"
            return execute_query(query)
        except Exception as e:
            raise ValidationError(f"Error al obtener todos los alumnos: {str(e)}")
    
    def save(self):
        try:
            query = "INSERT INTO alumnos (nombre, correo, fecha_ingreso) VALUES (%s, %s, %s)"
            return execute_query(query, (self.nombre, self.correo, self.fecha_ingreso))
        except Exception as e:
            raise ValidationError(f"Error al guardar alumno: {str(e)}")
    
    @staticmethod
    def get_all():
        try:
            query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos"
            return execute_query(query)
        except Exception as e:
            raise ValidationError(f"Error al obtener alumnos: {str(e)}")
    
    @staticmethod
    def get_by_id(alumno_id):
        try:
            alumno_id = parse_integer_field(alumno_id)
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
        try:
            alumno_id = parse_integer_field(alumno_id)
            if alumno_id is None or alumno_id <= 0:
                raise ValidationError("ID de alumno debe ser un entero positivo")
            
            nombre = validate_required_string(nombre, "nombre")
            correo = validate_email(correo)
            
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
        try:
            alumno_id = parse_integer_field(alumno_id)
            if alumno_id is None or alumno_id <= 0:
                raise ValidationError("ID de alumno debe ser un entero positivo")
            
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
        result = cls.get_by_id(alumno_id)
        if result:
            return {
                'id': result[0],
                'nombre': result[1], 
                'correo': result[2],
                'fecha_ingreso': result[3]
            }
        return None
    
    @classmethod
    def obtener_por_correo(cls, correo):
        try:
            query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos WHERE correo = %s"
            resultado = execute_query(query, (correo,))
            if resultado:
                fila = resultado[0]
                alumno = cls(fila[1], fila[2], fila[3])
                alumno.id = fila[0]
                return alumno
            return None
        except Exception as e:
            print(f"Error obteniendo alumno por correo: {e}")
            return None
