from db.database import execute_query

class Curso:
    def __init__(self, codigo, nombre, requisitos=None):
        self.codigo = codigo
        self.nombre = nombre
        self.requisitos = requisitos
    
    @classmethod
    def crear(cls, codigo, nombre, requisitos=None):
        """Crea un nuevo curso"""
        query = "INSERT INTO cursos (codigo, nombre, requisitos) VALUES (?, ?, ?)"
        id_curso = execute_query(query, (codigo, nombre, requisitos))
        return cls(codigo, nombre, requisitos)
    
    @classmethod
    def obtener_todos(cls):
        """Obtiene todos los cursos en formato consistente"""
        query = "SELECT id, codigo, nombre, requisitos FROM cursos ORDER BY codigo"
        return execute_query(query)
    
    def save(self):
        """Guarda un nuevo curso en la base de datos"""
        query = "INSERT INTO cursos (codigo, nombre, requisitos) VALUES (?, ?, ?)"
        return execute_query(query, (self.codigo, self.nombre, self.requisitos))
    
    @staticmethod
    def get_all():
        """Obtiene todos los cursos"""
        query = "SELECT id, codigo, nombre, requisitos FROM cursos"
        return execute_query(query)
    
    # Métodos de compatibilidad con nuevos modelos
    @classmethod
    def obtener_todos(cls):
        """Obtiene todos los cursos (método de compatibilidad)"""
        return cls.get_all()
    
    @classmethod
    def crear(cls, codigo, nombre, requisitos=None):
        """Crea un nuevo curso (método de compatibilidad)"""
        curso = cls(codigo, nombre, requisitos)
        curso_id = curso.save()
        return curso
    
    @staticmethod
    def get_by_id(curso_id):
        """Obtiene un curso por su ID"""
        query = "SELECT id, codigo, nombre, requisitos FROM cursos WHERE id = ?"
        results = execute_query(query, (curso_id,))
        return results[0] if results else None
    
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
