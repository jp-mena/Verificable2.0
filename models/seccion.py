# filepath: models/seccion.py
from db.database import execute_query

class Seccion:
    def __init__(self, id=None, numero=None, instancia_id=None):
        self.id = id
        self.numero = numero
        self.instancia_id = instancia_id

    @classmethod
    def crear(cls, numero, instancia_id):
        """Crea una nueva sección"""
        query = "INSERT INTO secciones (numero, instancia_id) VALUES (?, ?)"
        id_seccion = execute_query(query, (numero, instancia_id))
        return cls(id_seccion, numero, instancia_id)

    @classmethod
    def obtener_todos(cls):
        """Obtiene todas las secciones"""
        query = """
        SELECT s.id, s.numero, s.instancia_id, ic.semestre, ic.anio, c.codigo, c.nombre
        FROM secciones s
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        ORDER BY ic.anio DESC, ic.semestre DESC, s.numero
        """
        resultados = execute_query(query)
        return [
            {
                'id': fila[0],
                'numero': fila[1],
                'instancia_id': fila[2],
                'semestre': fila[3],
                'anio': fila[4],
                'curso_codigo': fila[5],
                'curso_nombre': fila[6]
            }
            for fila in resultados
        ]

    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene una sección por ID"""
        query = "SELECT id, numero, instancia_id FROM secciones WHERE id = ?"
        resultado = execute_query(query, (id,))
        if resultado:
            fila = resultado[0]
            return cls(fila[0], fila[1], fila[2])
        return None

    def actualizar(self):
        """Actualiza la sección"""
        query = "UPDATE secciones SET numero = ?, instancia_id = ? WHERE id = ?"
        execute_query(query, (self.numero, self.instancia_id, self.id))

    @classmethod
    def eliminar(cls, id):
        """Elimina una sección"""
        query = "DELETE FROM secciones WHERE id = ?"
        execute_query(query, (id,))
