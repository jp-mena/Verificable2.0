from sga.db.database import execute_query

class Inscripcion:
    def __init__(self, id=None, alumno_id=None, instancia_curso_id=None, fecha_inscripcion=None):
        self.id = id
        self.alumno_id = alumno_id
        self.instancia_curso_id = instancia_curso_id
        self.fecha_inscripcion = fecha_inscripcion
    
    @classmethod
    def crear(cls, alumno_id, instancia_curso_id, fecha_inscripcion=None):
        print(f"Debug crear: alumno_id={alumno_id}, instancia_curso_id={instancia_curso_id}, fecha_inscripcion={fecha_inscripcion}")
        
        if fecha_inscripcion:
            query = "INSERT INTO inscripciones (alumno_id, instancia_curso_id, fecha_inscripcion) VALUES (%s, %s, %s)"
            print(f"Debug: Usando query con fecha: {query}")
            print(f"Debug: Params: ({alumno_id}, {instancia_curso_id}, {fecha_inscripcion})")
            id_inscripcion = execute_query(query, (alumno_id, instancia_curso_id, fecha_inscripcion))
        else:
            query = "INSERT INTO inscripciones (alumno_id, instancia_curso_id) VALUES (%s, %s)"
            print(f"Debug: Usando query sin fecha: {query}")
            print(f"Debug: Params: ({alumno_id}, {instancia_curso_id})")
            id_inscripcion = execute_query(query, (alumno_id, instancia_curso_id))
        return cls(id_inscripcion, alumno_id, instancia_curso_id, fecha_inscripcion)

    @classmethod
    def obtener_todos(cls):
        query = """
        SELECT i.id, i.alumno_id, i.instancia_curso_id, i.fecha_inscripcion,
               a.nombre as alumno_nombre, a.correo as alumno_correo,
               c.codigo as curso_codigo, c.nombre as curso_nombre,
               ic.semestre, ic.anio
        FROM inscripciones i
        JOIN alumnos a ON i.alumno_id = a.id
        JOIN instancias_curso ic ON i.instancia_curso_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        ORDER BY i.fecha_inscripcion DESC
        """
        resultados = execute_query(query)
        return [
            {
                'id': fila[0],
                'alumno_id': fila[1],
                'instancia_curso_id': fila[2],
                'fecha_inscripcion': fila[3],
                'alumno_nombre': fila[4],
                'alumno_correo': fila[5],
                'curso_codigo': fila[6],
                'curso_nombre': fila[7],
                'semestre': fila[8],
                'anio': fila[9]            }
            for fila in resultados
        ]

    @classmethod
    def obtener_por_curso(cls, instancia_curso_id):
        query = """
        SELECT i.id, i.alumno_id, i.fecha_inscripcion,
               a.nombre, a.correo
        FROM inscripciones i
        JOIN alumnos a ON i.alumno_id = a.id
        WHERE i.instancia_curso_id = %s
        ORDER BY a.nombre
        """
        resultados = execute_query(query, (instancia_curso_id,))
        return [
            {
                'id': fila[0],
                'alumno_id': fila[1],
                'fecha_inscripcion': fila[2],
                'nombre': fila[3],
                'apellido': '',
                'rut': '',
                'email': fila[4]
            }
            for fila in resultados
        ]

    @classmethod
    def obtener_alumnos_no_inscritos(cls, instancia_curso_id):
        query = """
        SELECT a.id, a.nombre, a.correo
        FROM alumnos a
        WHERE a.id NOT IN (
            SELECT i.alumno_id 
            FROM inscripciones i 
            WHERE i.instancia_curso_id = %s
        )
        ORDER BY a.nombre
        """        
        resultados = execute_query(query, (instancia_curso_id,))
        return [
            {
                'id': fila[0],
                'nombre': fila[1],
                'correo': fila[2]
            }
            for fila in resultados
        ]

    @classmethod
    def eliminar(cls, id):
        query = "DELETE FROM inscripciones WHERE id = %s"
        execute_query(query, (id,))

    @classmethod
    def esta_inscrito(cls, alumno_id, instancia_curso_id):
        query = "SELECT COUNT(*) FROM inscripciones WHERE alumno_id = %s AND instancia_curso_id = %s"
        resultado = execute_query(query, (alumno_id, instancia_curso_id))
        return resultado[0][0] > 0
