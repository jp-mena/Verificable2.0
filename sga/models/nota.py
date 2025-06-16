# filepath: models/nota.py
from sga.db.database import execute_query

class Nota:
    def __init__(self, id=None, alumno_id=None, instancia_topico_id=None, nota=None):
        self.id = id
        self.alumno_id = alumno_id
        self.instancia_topico_id = instancia_topico_id
        self.nota = nota

    @classmethod
    def crear(cls, alumno_id, instancia_topico_id, nota):
        """Crea una nueva nota"""
        query = "INSERT INTO notas (alumno_id, instancia_topico_id, nota) VALUES (?, ?, ?)"
        id_nota = execute_query(query, (alumno_id, instancia_topico_id, nota))
        return cls(id_nota, alumno_id, instancia_topico_id, nota)

    @classmethod
    def obtener_todos(cls):
        """Obtiene todas las notas"""
        query = """
        SELECT n.id, n.alumno_id, n.instancia_topico_id, n.nota,
               a.nombre as alumno_nombre, a.correo as alumno_correo,
               it.nombre as instancia_nombre, it.peso,
               e.nombre as evaluacion_nombre, t.nombre as topico_nombre,
               s.numero, ic.semestre, ic.anio, c.codigo, ic.cerrado
        FROM notas n
        JOIN alumnos a ON n.alumno_id = a.id
        JOIN instancias_topico it ON n.instancia_topico_id = it.id
        JOIN evaluaciones e ON it.evaluacion_id = e.id
        JOIN topicos t ON it.topico_id = t.id
        JOIN secciones s ON e.seccion_id = s.id
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        ORDER BY ic.anio DESC, ic.semestre DESC, s.numero, a.nombre, e.nombre
        """
        resultados = execute_query(query)
        return [
            {
                'id': fila[0],
                'alumno_id': fila[1],
                'instancia_topico_id': fila[2],
                'nota': fila[3],
                'alumno_nombre': fila[4],
                'alumno_correo': fila[5],
                'instancia_nombre': fila[6],
                'peso': fila[7],
                'evaluacion_nombre': fila[8],
                'topico_nombre': fila[9],
                'seccion_numero': fila[10],
                'semestre': fila[11],
                'anio': fila[12],
                'curso_codigo': fila[13],
                'curso_cerrado': bool(fila[14]) if fila[14] is not None else False
            }
            for fila in resultados
        ]

    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene una nota por ID"""
        query = "SELECT id, alumno_id, instancia_topico_id, nota FROM notas WHERE id = ?"
        resultado = execute_query(query, (id,))
        if resultado:
            fila = resultado[0]
            return cls(fila[0], fila[1], fila[2], fila[3])
        return None

    @classmethod
    def obtener_por_alumno(cls, alumno_id):
        """Obtiene todas las notas de un alumno"""
        query = "SELECT id, alumno_id, instancia_topico_id, nota FROM notas WHERE alumno_id = ?"
        resultados = execute_query(query, (alumno_id,))
        return [cls(fila[0], fila[1], fila[2], fila[3]) for fila in resultados]

    def actualizar(self):
        """Actualiza la nota"""
        query = "UPDATE notas SET alumno_id = ?, instancia_topico_id = ?, nota = ? WHERE id = ?"
        execute_query(query, (self.alumno_id, self.instancia_topico_id, self.nota, self.id))

    @classmethod
    def eliminar(cls, id):
        """Elimina una nota"""
        query = "DELETE FROM notas WHERE id = ?"
        execute_query(query, (id,))
