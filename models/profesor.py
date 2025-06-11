from db.database import execute_query

class Profesor:
    def __init__(self, nombre, correo):
        self.nombre = nombre
        self.correo = correo
    
    def save(self):
        """Guarda un nuevo profesor en la base de datos"""
        query = "INSERT INTO profesores (nombre, correo) VALUES (?, ?)"
        return execute_query(query, (self.nombre, self.correo))
    
    @staticmethod
    def get_all():
        """Obtiene todos los profesores"""
        query = "SELECT id, nombre, correo FROM profesores"
        return execute_query(query)
    
    @classmethod
    def obtener_todos(cls):
        """Obtiene todos los profesores (método de compatibilidad)"""
        return cls.get_all()
    
    @classmethod
    def crear(cls, nombre, correo):
        """Crea un nuevo profesor (método de compatibilidad)"""
        profesor = cls(nombre, correo)
        profesor_id = profesor.save()
        return profesor
    
    @staticmethod
    def get_by_id(profesor_id):
        """Obtiene un profesor por su ID"""
        query = "SELECT id, nombre, correo FROM profesores WHERE id = ?"
        results = execute_query(query, (profesor_id,))
        return results[0] if results else None
    
    @staticmethod
    def get_by_correo(correo):
        """Obtiene un profesor por su correo"""
        query = "SELECT id, nombre, correo FROM profesores WHERE correo = ?"
        results = execute_query(query, (correo,))
        return results[0] if results else None
    
    @staticmethod
    def update(profesor_id, nombre, correo):
        """Actualiza un profesor existente"""
        query = "UPDATE profesores SET nombre = ?, correo = ? WHERE id = ?"
        return execute_query(query, (nombre, correo, profesor_id))
    
    @staticmethod
    def delete(profesor_id):
        """Elimina un profesor"""
        query = "DELETE FROM profesores WHERE id = ?"
        return execute_query(query, (profesor_id,))
