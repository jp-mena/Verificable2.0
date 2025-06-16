from sga.db.database import execute_query
from sga.utils.validators import ValidationError, safe_int_conversion, validate_required_string
import re

class Curso:
    def __init__(self, codigo, nombre, requisitos=None):
        self.codigo = self._validate_codigo(codigo)
        self.nombre = validate_required_string(nombre, "nombre")
        self.requisitos = requisitos.strip() if requisitos else None
    
    def _validate_codigo(self, codigo):
        """Valida el código del curso"""
        codigo = validate_required_string(codigo, "código")
        
        # Validar formato del código (letras seguidas de números, ej: ICC3030)
        if not re.match(r'^[A-Z]{2,5}\d{4}$', codigo.upper()):
            raise ValidationError("Código debe tener formato: 2-5 letras seguidas de 4 números (ej: ICC3030)")
        
        return codigo.upper()
    @classmethod
    def crear(cls, codigo, nombre, requisitos=None):
        """Crea un nuevo curso"""
        try:
            curso = cls(codigo, nombre, requisitos)
            query = "INSERT INTO cursos (codigo, nombre, requisitos) VALUES (?, ?, ?)"
            id_curso = execute_query(query, (curso.codigo, curso.nombre, curso.requisitos))
            return curso
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al crear curso: {str(e)}")
    
    @classmethod
    def obtener_todos(cls):
        """Obtiene todos los cursos en formato consistente"""
        try:
            query = "SELECT id, codigo, nombre, requisitos FROM cursos ORDER BY codigo"
            return execute_query(query)
        except Exception as e:
            raise ValidationError(f"Error al obtener todos los cursos: {str(e)}")
    
    def save(self):
        """Guarda un nuevo curso en la base de datos"""
        try:
            query = "INSERT INTO cursos (codigo, nombre, requisitos) VALUES (?, ?, ?)"
            return execute_query(query, (self.codigo, self.nombre, self.requisitos))
        except Exception as e:
            raise ValidationError(f"Error al guardar curso: {str(e)}")
    
    @staticmethod
    def get_all():
        """Obtiene todos los cursos"""
        try:
            query = "SELECT id, codigo, nombre, requisitos FROM cursos"
            return execute_query(query)
        except Exception as e:
            raise ValidationError(f"Error al obtener cursos: {str(e)}")
    
    @staticmethod
    def get_by_id(curso_id):
        """Obtiene un curso por su ID"""
        try:
            curso_id = safe_int_conversion(curso_id)
            if curso_id is None or curso_id <= 0:
                raise ValidationError("ID de curso debe ser un entero positivo")
            
            query = "SELECT id, codigo, nombre, requisitos FROM cursos WHERE id = ?"
            results = execute_query(query, (curso_id,))
            return results[0] if results else None
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al obtener curso por ID: {str(e)}")
    
    @staticmethod
    def get_by_codigo(codigo):
        """Obtiene un curso por su código"""
        try:
            if not codigo:
                raise ValidationError("Código de curso es requerido")
            
            query = "SELECT id, codigo, nombre, requisitos FROM cursos WHERE codigo = ?"
            results = execute_query(query, (codigo.upper(),))
            return results[0] if results else None
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al obtener curso por código: {str(e)}")
    
    @staticmethod
    def update(curso_id, codigo, nombre, requisitos=None):
        """Actualiza un curso existente"""
        try:
            curso_id = safe_int_conversion(curso_id)
            if curso_id is None or curso_id <= 0:
                raise ValidationError("ID de curso debe ser un entero positivo")
            
            # Crear objeto temporal para validar
            temp_curso = Curso(codigo, nombre, requisitos)
            
            query = "UPDATE cursos SET codigo = ?, nombre = ?, requisitos = ? WHERE id = ?"
            execute_query(query, (temp_curso.codigo, temp_curso.nombre, temp_curso.requisitos, curso_id))
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al actualizar curso: {str(e)}")
    
    @staticmethod
    def delete(curso_id):
        """Elimina un curso"""
        try:
            curso_id = safe_int_conversion(curso_id)
            if curso_id is None or curso_id <= 0:
                raise ValidationError("ID de curso debe ser un entero positivo")
            
            # Verificar si el curso existe
            existing = Curso.get_by_id(curso_id)
            if not existing:
                raise ValidationError("Curso no encontrado")
            
            query = "DELETE FROM cursos WHERE id = ?"
            execute_query(query, (curso_id,))
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al eliminar curso: {str(e)}")
    
    @staticmethod
    def get_by_codigo(codigo):
        """Obtiene un curso por su código"""
        query = "SELECT id, codigo, nombre, requisitos FROM cursos WHERE codigo = ?"
        results = execute_query(query, (codigo,))
        return results[0] if results else None
    
    @staticmethod
    def update(curso_id, codigo, nombre, requisitos):
        """Actualiza un curso existente"""
        query = "UPDATE cursos SET codigo = ?, nombre = ?, requisitos = ? WHERE id = ?"
        return execute_query(query, (codigo, nombre, requisitos, curso_id))
    
    @staticmethod
    def delete(curso_id):
        """Elimina un curso"""
        query = "DELETE FROM cursos WHERE id = ?"
        return execute_query(query, (curso_id,))
