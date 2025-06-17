from sga.db.database import execute_query
from sga.utils.validators import ValidationError, safe_int_conversion, validate_required_string
import re

class Curso:
    def __init__(self, codigo, nombre, creditos=4, requisitos=None):
        self.codigo = self._validate_codigo(codigo)
        self.nombre = validate_required_string(nombre, "nombre")
        self.creditos = self._validate_creditos(creditos)
        self.requisitos = self._process_requisitos(requisitos)
    
    def _validate_codigo(self, codigo):
        """Valida el código del curso"""
        codigo = validate_required_string(codigo, "código")
        
        # Validar formato del código (letras seguidas de números, ej: ICC3030)
        if not re.match(r'^[A-Z]{2,5}\d{4}$', codigo.upper()):
            raise ValidationError("Código debe tener formato: 2-5 letras seguidas de 4 números (ej: ICC3030)")
        
        return codigo.upper()
    
    def _validate_creditos(self, creditos):
        """Valida la cantidad de créditos"""
        if creditos is None:
            return 4  # Valor por defecto
            
        try:
            creditos_int = int(creditos)
            if creditos_int < 1 or creditos_int > 12:
                raise ValidationError("Los créditos deben estar entre 1 y 12")
            return creditos_int
        except (ValueError, TypeError):
            raise ValidationError("Los créditos deben ser un número entero")
    
    def _process_requisitos(self, requisitos):
        """Procesa los requisitos: puede ser lista de códigos o string separado por comas"""
        if not requisitos:
            return None
            
        if isinstance(requisitos, list):
            # Ya es una lista de códigos
            requisitos_clean = [codigo.strip().upper() for codigo in requisitos if codigo.strip()]
            return ','.join(requisitos_clean) if requisitos_clean else None
        
        if isinstance(requisitos, str):
            # String separado por comas
            requisitos_clean = [codigo.strip().upper() for codigo in requisitos.split(',') if codigo.strip()]
            return ','.join(requisitos_clean) if requisitos_clean else None
            
        return None
    
    def get_requisitos_list(self):
        """Obtiene los requisitos como lista de códigos"""
        if not self.requisitos:
            return []
        return [codigo.strip() for codigo in self.requisitos.split(',') if codigo.strip()]
    
    def save(self):
        """Guarda un nuevo curso en la base de datos"""
        try:
            query = "INSERT INTO cursos (codigo, nombre, creditos, requisitos) VALUES (?, ?, ?, ?)"
            return execute_query(query, (self.codigo, self.nombre, self.creditos, self.requisitos))
        except Exception as e:
            raise ValidationError(f"Error al guardar curso: {str(e)}")
    
    @staticmethod
    def get_all():
        """Obtiene todos los cursos"""
        try:
            query = "SELECT id, codigo, nombre, creditos, requisitos FROM cursos ORDER BY codigo"
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
            
            query = "SELECT id, codigo, nombre, creditos, requisitos FROM cursos WHERE id = ?"
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
            
            query = "SELECT id, codigo, nombre, creditos, requisitos FROM cursos WHERE codigo = ?"
            results = execute_query(query, (codigo.upper(),))
            return results[0] if results else None        
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al obtener curso por código: {str(e)}")
    
    @staticmethod
    def update(curso_id, codigo, nombre, creditos=4, requisitos=None):
        """Actualiza un curso existente"""
        try:
            curso_id = safe_int_conversion(curso_id)
            if curso_id is None or curso_id <= 0:
                raise ValidationError("ID de curso debe ser un entero positivo")
            
            # Crear objeto temporal para validar
            temp_curso = Curso(codigo, nombre, creditos, requisitos)
            
            query = "UPDATE cursos SET codigo = ?, nombre = ?, creditos = ?, requisitos = ? WHERE id = ?"
            execute_query(query, (temp_curso.codigo, temp_curso.nombre, temp_curso.creditos, temp_curso.requisitos, curso_id))
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
    def get_prerequisitos_disponibles():
        """Obtiene lista de cursos disponibles como prerrequisitos"""
        try:
            query = "SELECT codigo, nombre FROM cursos ORDER BY codigo"
            results = execute_query(query)
            return [{'codigo': row[0], 'nombre': row[1]} for row in results]
        except Exception as e:
            raise ValidationError(f"Error al obtener prerrequisitos: {str(e)}")
    
    @staticmethod
    def get_requisitos_as_list(requisitos_str):
        """Convierte string de requisitos a lista"""
        if not requisitos_str:
            return []
        return [codigo.strip() for codigo in requisitos_str.split(',') if codigo.strip()]
    
    @staticmethod
    def validate_requisitos(requisitos_list, curso_codigo=None):
        """Valida que los códigos de prerrequisitos existan y no haya ciclos"""
        if not requisitos_list:
            return True
            
        for codigo in requisitos_list:
            # No puede ser prerrequisito de sí mismo
            if curso_codigo and codigo.upper() == curso_codigo.upper():
                raise ValidationError(f"Un curso no puede ser prerrequisito de sí mismo")
                
            # Verificar que el curso existe
            existing = Curso.get_by_codigo(codigo)
            if not existing:
                raise ValidationError(f"El curso prerrequisito {codigo} no existe")
        
        return True
