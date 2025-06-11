# filepath: models/topico.py
from db.database import execute_query

class Topico:
    def __init__(self, id=None, nombre=None, tipo=None):
        self.id = id
        self.nombre = nombre
        self.tipo = tipo  # control, tarea, actividad, etc.

    @classmethod
    def crear(cls, nombre, tipo):
        """Crea un nuevo tópico"""
        query = "INSERT INTO topicos (nombre, tipo) VALUES (?, ?)"
        id_topico = execute_query(query, (nombre, tipo))
        return cls(id_topico, nombre, tipo)

    @classmethod
    def obtener_todos(cls):
        """Obtiene todos los tópicos"""
        query = "SELECT id, nombre, tipo FROM topicos ORDER BY tipo, nombre"
        resultados = execute_query(query)
        return [
            {
                'id': fila[0],
                'nombre': fila[1],
                'tipo': fila[2]
            }
            for fila in resultados
        ]

    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene un tópico por ID"""
        query = "SELECT id, nombre, tipo FROM topicos WHERE id = ?"
        resultado = execute_query(query, (id,))
        if resultado:
            fila = resultado[0]
            return cls(fila[0], fila[1], fila[2])
        return None

    def actualizar(self):
        """Actualiza el tópico"""
        query = "UPDATE topicos SET nombre = ?, tipo = ? WHERE id = ?"
        execute_query(query, (self.nombre, self.tipo, self.id))

    @classmethod
    def eliminar(cls, id):
        """Elimina un tópico"""
        query = "DELETE FROM topicos WHERE id = ?"
        execute_query(query, (id,))
