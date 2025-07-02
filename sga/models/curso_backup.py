from sga.db.database import execute_query
from sga.utils.validators import ValidationError, parse_integer_field, validate_required_string
import re

class Curso:
    def __init__(self, codigo, nombre, creditos=4, requisitos=None):
        self.codigo = self._validate_codigo(codigo)
        self.nombre = validate_required_string(nombre, "nombre")
        self.creditos = self._validate_creditos(creditos)
        self.requisitos = self._process_requisitos(requisitos)
    
    def _validate_codigo(self, codigo):
        codigo = validate_required_string(codigo, "código")
        
        if not re.match(r'^[A-Z]{2,5}\d{4}$', codigo.upper()):
            raise ValidationError("Código debe tener formato: 2-5 letras seguidas de 4 números (ej: ICC3030)")
        
        return codigo.upper()
    
    def _validate_creditos(self, creditos):
        if creditos is None:  return 4
            
        try:
            creditos_int = int(creditos)
            if creditos_int < 1 or creditos_int > 12:
                raise ValidationError("Los créditos deben estar entre 1 y 12")
            return creditos_int
        except (ValueError, TypeError):
            raise ValidationError("Los créditos deben ser un número entero")
    
    def _process_requisitos(self, requisitos):
        if not requisitos:
            return None
            
        if isinstance(requisitos, list):
            requisitos_clean = [codigo.strip().upper() for codigo in requisitos if codigo.strip()]
            return ','.join(requisitos_clean) if requisitos_clean else None
        
        if isinstance(requisitos, str):
            requisitos_clean = [codigo.strip().upper() for codigo in requisitos.split(',') if codigo.strip()]
            return ','.join(requisitos_clean) if requisitos_clean else None
            
        return None
    
    def get_requisitos_list(self):
        if not self.requisitos:
            return []        
        return [codigo.strip() for codigo in self.requisitos.split(',') if codigo.strip()]
    
    def save(self):
        try:
            query = "INSERT INTO cursos (codigo, nombre, creditos, requisitos) VALUES (%s, %s, %s, %s)"
            return execute_query(query, (self.codigo, self.nombre, self.creditos, self.requisitos))
        except Exception as e:
            raise ValidationError(f"Error al guardar curso: {str(e)}")
    
    @classmethod
    def get_all(cls):
        try:
            query = "SELECT id, codigo, nombre, creditos, requisitos FROM cursos ORDER BY codigo"
            resultados = execute_query(query)
            cursos = []
            for fila in resultados:
                curso = cls(fila[1], fila[2], fila[3], fila[4])
                curso.id = fila[0]
                cursos.append(curso)
            return cursos
        except Exception as e:
            raise ValidationError(f"Error al obtener cursos: {str(e)}")
    @classmethod
    def get_by_id(cls, curso_id):
        try:
            curso_id = parse_integer_field(curso_id)
            if curso_id is None or curso_id <= 0:
                raise ValidationError("ID de curso debe ser un entero positivo")
            
            query = "SELECT id, codigo, nombre, creditos, requisitos FROM cursos WHERE id = %s"
            results = execute_query(query, (curso_id,))
            if results:
                fila = results[0]
                curso = cls(fila[1], fila[2], fila[3], fila[4])
                curso.id = fila[0]
                return curso
            return None
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al obtener curso por ID: {str(e)}")
    
    @classmethod
    def get_by_codigo(cls, codigo):
        try:
            if not codigo:
                raise ValidationError("Código de curso es requerido")
            
            query = "SELECT id, codigo, nombre, creditos, requisitos FROM cursos WHERE codigo = %s"
            results = execute_query(query, (codigo.upper(),))
            if results:
                fila = results[0]
                curso = cls(fila[1], fila[2], fila[3], fila[4])
                curso.id = fila[0]
                return curso
            return None        
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al obtener curso por código: {str(e)}")
    
    @classmethod
    def obtener_por_codigo(cls, codigo):
        try:
            query = "SELECT id, codigo, nombre, creditos, requisitos FROM cursos WHERE codigo = %s"
            resultado = execute_query(query, (codigo,))
            if resultado:
                fila = resultado[0]
                curso = cls(fila[1], fila[2], fila[3], fila[4])
                curso.id = fila[0]
                return curso
            return None
        except Exception as e:
            print(f"Error obteniendo curso por código: {e}")
            return None
    
    @staticmethod
    def update(curso_id, codigo, nombre, creditos=4, requisitos=None):
        try:
            curso_id = parse_integer_field(curso_id)
            if curso_id is None or curso_id <= 0:
                raise ValidationError("ID de curso debe ser un entero positivo")
            
            temp_curso = Curso(codigo, nombre, creditos, requisitos)
            
            query = "UPDATE cursos SET codigo = %s, nombre = %s, creditos = %s, requisitos = %s WHERE id = %s"
            execute_query(query, (temp_curso.codigo, temp_curso.nombre, temp_curso.creditos, temp_curso.requisitos, curso_id))
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al actualizar curso: {str(e)}")
    
    @staticmethod
    def delete(curso_id):
        try:
            curso_id = parse_integer_field(curso_id)
            if curso_id is None or curso_id <= 0:
                raise ValidationError("ID de curso debe ser un entero positivo")
            
            existing = Curso.get_by_id(curso_id)
            if not existing:
                raise ValidationError("Curso no encontrado")
            
            query = "DELETE FROM cursos WHERE id = %s"
            execute_query(query, (curso_id,))
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al eliminar curso: {str(e)}")
    
    @staticmethod
    def get_prerequisitos_disponibles():
        try:
            query = "SELECT codigo, nombre FROM cursos ORDER BY codigo"
            results = execute_query(query)
            return [{'codigo': row[0], 'nombre': row[1]} for row in results]
        except Exception as e:
            raise ValidationError(f"Error al obtener prerrequisitos: {str(e)}")
    
    @staticmethod
    def get_requisitos_as_list(requisitos_str):
        if not requisitos_str:
            return []
        return [codigo.strip() for codigo in requisitos_str.split(',') if codigo.strip()]
    
    @staticmethod
    def validate_requisitos(requisitos_list, curso_codigo=None):
       
        if not requisitos_list:
            return
            
        for codigo in requisitos_list:
            if curso_codigo and codigo.upper() == curso_codigo.upper():
                raise ValidationError(f"Un curso no puede ser prerrequisito de sí mismo")
                
            existing = Curso.get_by_codigo(codigo)
            if not existing:
                raise ValidationError(f"El curso prerrequisito {codigo} no existe")
