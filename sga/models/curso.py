from sga.db.database import execute_query
from sga.utils.validators import ValidationError, safe_int_conversion, validate_required_string
import re

class Curso:
    def __init__(self, codigo, nombre, creditos=4, requisitos=None):
        self.codigo = self._validate_codigo(codigo)
        self.nombre = validate_required_string(nombre, "nombre", 100)  # Máximo 100 caracteres
        self.creditos = self._validate_creditos(creditos)
        self.requisitos = self._process_requisitos(requisitos)
    
    def _validate_codigo(self, codigo):
        """Valida el código del curso"""
        codigo = validate_required_string(codigo, "código", 20)  # Máximo 20 caracteres
        
        # Validar longitud máxima (evitar códigos excesivamente largos)
        if len(codigo) > 20:
            raise ValidationError("El código del curso no puede exceder 20 caracteres")
        
        # Validar que no contenga espacios
        if ' ' in codigo:
            raise ValidationError("El código del curso no puede contener espacios")
        
        # Validar que solo contenga caracteres alfanuméricos
        if not re.match(r'^[A-Za-z0-9]+$', codigo):
            raise ValidationError("El código del curso solo puede contener letras y números")
        
        # Validar formato del código (letras seguidas de números, ej: ICC3030)
        if not re.match(r'^[A-Z]{2,5}\d{3,4}$', codigo.upper()):
            raise ValidationError("Código debe tener formato: 2-5 letras seguidas de 3-4 números (ej: ICC3030, TEST101)")
        
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
            # Verificar que no exista un curso con el mismo código
            existing_curso = self.get_by_codigo(self.codigo)
            if existing_curso:
                raise ValidationError(f"Ya existe un curso con el código {self.codigo}")
            
            query = "INSERT INTO cursos (codigo, nombre, creditos, requisitos) VALUES (%s, %s, %s, %s)"
            return execute_query(query, (self.codigo, self.nombre, self.creditos, self.requisitos))
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al guardar curso: {str(e)}")
    
    @classmethod
    def get_all(cls):
        """Obtiene todos los cursos"""
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
        """Obtiene un curso por su ID"""
        try:
            curso_id = safe_int_conversion(curso_id)
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
        """Obtiene un curso por su código"""
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
        """Obtiene un curso por su código (método alternativo para compatibilidad)"""
        return cls.get_by_codigo(codigo)
    
    @staticmethod
    def delete(curso_id):
        """Elimina un curso por su ID"""
        try:
            curso_id = safe_int_conversion(curso_id)
            if curso_id is None or curso_id <= 0:
                raise ValidationError("ID de curso debe ser un entero positivo")
            
            query = "DELETE FROM cursos WHERE id = %s"
            return execute_query(query, (curso_id,))
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al eliminar curso: {str(e)}")
    
    def update(self):
        """Actualiza un curso existente"""
        try:
            if not hasattr(self, 'id') or not self.id:
                raise ValidationError("ID de curso es requerido para actualizar")
            
            query = "UPDATE cursos SET codigo = %s, nombre = %s, creditos = %s, requisitos = %s WHERE id = %s"
            return execute_query(query, (self.codigo, self.nombre, self.creditos, self.requisitos, self.id))
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al actualizar curso: {str(e)}")
    
    def to_dict(self):
        """Convierte el curso a diccionario"""
        result = {
            'codigo': self.codigo,
            'nombre': self.nombre,
            'creditos': self.creditos,
            'requisitos': self.get_requisitos_list()
        }
        if hasattr(self, 'id'):
            result['id'] = self.id
        return result
    
    def __str__(self):
        return f"Curso({self.codigo}: {self.nombre})"
    
    def __repr__(self):
        return f"Curso(codigo='{self.codigo}', nombre='{self.nombre}', creditos={self.creditos})"
    @classmethod
    def get_prerequisitos_disponibles(cls):
        """Obtiene todos los cursos disponibles como prerequisitos"""
        try:
            cursos = cls.get_all()
            return [curso.to_dict() for curso in cursos]
        except Exception as e:
            print(f"Error obteniendo prerequisitos: {e}")
            return []
    
    @staticmethod
    def get_requisitos_as_list(requisitos_str):
        """Convierte una cadena de requisitos en lista"""
        if not requisitos_str:
            return []
        return [req.strip() for req in requisitos_str.split(',') if req.strip()]
    
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
