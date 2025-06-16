from db.database import execute_query

class Alumno:
    def __init__(self, nombre, correo, fecha_ingreso):
        self.nombre = nombre
        self.correo = correo
        self.fecha_ingreso = fecha_ingreso
    
    @classmethod
    def crear(cls, nombre, correo, fecha_ingreso):
        """Crea un nuevo alumno"""
        query = "INSERT INTO alumnos (nombre, correo, fecha_ingreso) VALUES (?, ?, ?)"
        id_alumno = execute_query(query, (nombre, correo, fecha_ingreso))
        return cls(nombre, correo, fecha_ingreso)
    
    @classmethod
    def obtener_todos(cls):
        """Obtiene todos los alumnos en formato consistente"""
        query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos ORDER BY nombre"
        return execute_query(query)
    
    def save(self):
        """Guarda un nuevo alumno en la base de datos"""
        query = "INSERT INTO alumnos (nombre, correo, fecha_ingreso) VALUES (?, ?, ?)"
        return execute_query(query, (self.nombre, self.correo, self.fecha_ingreso))
    
    @staticmethod
    def get_all():
        """Obtiene todos los alumnos"""
        query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos"
        return execute_query(query)
    
    @classmethod
    def obtener_todos(cls):
        """Obtiene todos los alumnos (método de compatibilidad)"""
        return cls.get_all()
    
    @classmethod
    def crear(cls, nombre, correo, fecha_ingreso):
        """Crea un nuevo alumno (método de compatibilidad)"""
        alumno = cls(nombre, correo, fecha_ingreso)
        alumno_id = alumno.save()
        return alumno
    
    @staticmethod
    def get_by_id(alumno_id):
        """Obtiene un alumno por su ID"""
        query = "SELECT id, nombre, correo, fecha_ingreso FROM alumnos WHERE id = ?"
        results = execute_query(query, (alumno_id,))
        return results[0] if results else None
    
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
