# filepath: models/evaluacion.py
from db.database import execute_query

class Evaluacion:
    def __init__(self, id=None, nombre=None, porcentaje=None, seccion_id=None):
        self.id = id
        self.nombre = nombre
        self.porcentaje = porcentaje
        self.seccion_id = seccion_id

    @classmethod
    def crear(cls, nombre, porcentaje, seccion_id):
        """Crea una nueva evaluación"""
        query = "INSERT INTO evaluaciones (nombre, porcentaje, seccion_id) VALUES (?, ?, ?)"
        id_evaluacion = execute_query(query, (nombre, porcentaje, seccion_id))
        return cls(id_evaluacion, nombre, porcentaje, seccion_id)

    @classmethod
    def obtener_todos(cls):
        """Obtiene todas las evaluaciones"""
        query = """
        SELECT e.id, e.nombre, e.porcentaje, e.seccion_id, s.numero, 
               ic.semestre, ic.anio, c.codigo, c.nombre, ic.cerrado
        FROM evaluaciones e
        JOIN secciones s ON e.seccion_id = s.id
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        ORDER BY ic.anio DESC, ic.semestre DESC, s.numero, e.nombre
        """
        resultados = execute_query(query)
        return [
            {
                'id': fila[0],
                'nombre': fila[1],
                'porcentaje': fila[2],
                'seccion_id': fila[3],
                'seccion_numero': fila[4],
                'semestre': fila[5],
                'anio': fila[6],
                'curso_codigo': fila[7],
                'curso_nombre': fila[8],
                'curso_cerrado': bool(fila[9])
            }
            for fila in resultados
        ]

    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene una evaluación por ID"""
        query = "SELECT id, nombre, porcentaje, seccion_id FROM evaluaciones WHERE id = ?"
        resultado = execute_query(query, (id,))
        if resultado:
            fila = resultado[0]
            return cls(fila[0], fila[1], fila[2], fila[3])
        return None

    @classmethod
    def obtener_por_seccion(cls, seccion_id):
        """Obtiene todas las evaluaciones de una sección"""
        query = "SELECT id, nombre, porcentaje, seccion_id FROM evaluaciones WHERE seccion_id = ?"
        resultados = execute_query(query, (seccion_id,))
        return [cls(fila[0], fila[1], fila[2], fila[3]) for fila in resultados]

    def actualizar(self):
        """Actualiza la evaluación"""
        query = "UPDATE evaluaciones SET nombre = ?, porcentaje = ?, seccion_id = ? WHERE id = ?"
        execute_query(query, (self.nombre, self.porcentaje, self.seccion_id, self.id))

    @classmethod
    def eliminar(cls, id):
        """Elimina una evaluación"""
        query = "DELETE FROM evaluaciones WHERE id = ?"
        execute_query(query, (id,))
