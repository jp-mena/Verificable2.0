# filepath: models/instancia_curso.py
from db.database import execute_query

class InstanciaCurso:
    def __init__(self, id=None, semestre=None, anio=None, curso_id=None):
        self.id = id
        self.semestre = semestre
        self.anio = anio
        self.curso_id = curso_id

    @classmethod
    def crear(cls, semestre, anio, curso_id):
        """Crea una nueva instancia de curso"""
        query = "INSERT INTO instancias_curso (semestre, anio, curso_id) VALUES (?, ?, ?)"
        id_instancia = execute_query(query, (semestre, anio, curso_id))
        return cls(id_instancia, semestre, anio, curso_id)

    @classmethod
    def obtener_todos(cls):
        """Obtiene todas las instancias de curso"""
        query = """
        SELECT ic.id, ic.semestre, ic.anio, ic.curso_id, c.codigo, c.nombre 
        FROM instancias_curso ic
        JOIN cursos c ON ic.curso_id = c.id
        ORDER BY ic.anio DESC, ic.semestre DESC
        """
        resultados = execute_query(query)
        return [
            {
                'id': fila[0],
                'semestre': fila[1], 
                'anio': fila[2],
                'curso_id': fila[3],
                'curso_codigo': fila[4],
                'curso_nombre': fila[5]
            }
            for fila in resultados
        ]

    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene una instancia de curso por ID"""
        query = "SELECT id, semestre, anio, curso_id FROM instancias_curso WHERE id = ?"
        resultado = execute_query(query, (id,))
        if resultado:
            fila = resultado[0]
            return cls(fila[0], fila[1], fila[2], fila[3])
        return None

    def actualizar(self):
        """Actualiza la instancia de curso"""
        query = "UPDATE instancias_curso SET semestre = ?, anio = ?, curso_id = ? WHERE id = ?"
        execute_query(query, (self.semestre, self.anio, self.curso_id, self.id))

    @classmethod
    def eliminar(cls, id):
        """Elimina una instancia de curso"""
        query = "DELETE FROM instancias_curso WHERE id = ?"
        execute_query(query, (id,))
