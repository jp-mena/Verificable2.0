from db.database import execute_query

class Alumno:
    def __init__(self, nombre, correo, fecha_ingreso):
        self.nombre = nombre
        self.correo = correo
        self.fecha_ingreso = fecha_ingreso
    
    def save(self):
        """Guarda un nuevo alumno en la base de datos"""
        query = "INSERT INTO alumnos (nombre, correo, fecha_ingreso) VALUES (?, ?, ?)"
        return execute_query(query, (self.nombre, self.correo, self.fecha_ingreso))
    
    @staticmethod
    def get_all():
        """Obtiene todos los alumnos"""
        query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos"
        return execute_query(query)
    
    @staticmethod
    def get_by_id(alumno_id):
        """Obtiene un alumno por su ID"""
        query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos WHERE id = ?"
        results = execute_query(query, (alumno_id,))
        return results[0] if results else None
    
    @staticmethod
    def get_by_correo(correo):
        """Obtiene un alumno por su correo"""
        query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos WHERE correo = ?"
        results = execute_query(query, (correo,))
        return results[0] if results else None
    
    @staticmethod
    def update(alumno_id, nombre, correo, fecha_ingreso):
        """Actualiza un alumno existente"""
        query = "UPDATE alumnos SET nombre = ?, correo = ?, fecha_ingreso = ? WHERE id = ?"
        return execute_query(query, (nombre, correo, fecha_ingreso, alumno_id))
    
    @staticmethod
    def delete(alumno_id):
        """Elimina un alumno"""
        query = "DELETE FROM alumnos WHERE id = ?"
        return execute_query(query, (alumno_id,))
