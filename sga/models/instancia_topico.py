# filepath: models/instancia_topico.py
from sga.db.database import execute_query

class InstanciaTopico:
    def __init__(self, id=None, nombre=None, peso=None, opcional=None, evaluacion_id=None, topico_id=None):
        self.id = id
        self.nombre = nombre
        self.peso = peso  # peso individual dentro de la evaluación
        self.opcional = opcional  # boolean
        self.evaluacion_id = evaluacion_id
        self.topico_id = topico_id

    @classmethod
    def crear(cls, nombre, opcional, evaluacion_id, topico_id):
        """Crea una nueva instancia de tópico"""
        # Obtener el peso de la evaluación automáticamente
        query_peso = "SELECT porcentaje FROM evaluaciones WHERE id = %s"
        resultado_peso = execute_query(query_peso, (evaluacion_id,))
        peso = float(resultado_peso[0][0]) if resultado_peso else 0.0
        
        query = "INSERT INTO instancias_topico (nombre, peso, opcional, evaluacion_id, topico_id) VALUES (%s, %s, %s, %s, %s)"
        id_instancia = execute_query(query, (nombre, peso, opcional, evaluacion_id, topico_id))
        return cls(id_instancia, nombre, peso, opcional, evaluacion_id, topico_id)

    @classmethod
    def obtener_todos(cls):
        """Obtiene todas las instancias de tópico"""
        query = """
        SELECT it.id, it.nombre, it.peso, it.opcional, it.evaluacion_id, it.topico_id,
               e.nombre as evaluacion_nombre, t.nombre as topico_nombre, t.tipo,
               s.numero, ic.semestre, ic.anio, c.codigo, ic.cerrado
        FROM instancias_topico it
        JOIN evaluaciones e ON it.evaluacion_id = e.id
        JOIN topicos t ON it.topico_id = t.id
        JOIN secciones s ON e.seccion_id = s.id
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        ORDER BY ic.anio DESC, ic.semestre DESC, s.numero, e.nombre, it.nombre
        """
        resultados = execute_query(query)
        return [
            {
                'id': fila[0],
                'nombre': fila[1],
                'peso': fila[2],
                'opcional': bool(fila[3]),
                'evaluacion_id': fila[4],
                'topico_id': fila[5],
                'evaluacion_nombre': fila[6],
                'topico_nombre': fila[7],
                'topico_tipo': fila[8],
                'seccion_numero': fila[9],
                'semestre': fila[10],
                'anio': fila[11],
                'curso_codigo': fila[12],
                'curso_cerrado': bool(fila[13])
            }
            for fila in resultados
        ]

    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene una instancia de tópico por ID"""
        query = "SELECT id, nombre, peso, opcional, evaluacion_id, topico_id FROM instancias_topico WHERE id = %s"
        resultado = execute_query(query, (id,))
        if resultado:
            fila = resultado[0]
            return cls(fila[0], fila[1], fila[2], bool(fila[3]), fila[4], fila[5])
        return None

    def actualizar(self):
        """Actualiza la instancia de tópico"""
        # Actualizar el peso automáticamente desde la evaluación
        query_peso = "SELECT porcentaje FROM evaluaciones WHERE id = %s"
        resultado_peso = execute_query(query_peso, (self.evaluacion_id,))
        if resultado_peso:
            self.peso = float(resultado_peso[0][0])
        
        query = "UPDATE instancias_topico SET nombre = %s, peso = %s, opcional = %s, evaluacion_id = %s, topico_id = %s WHERE id = %s"
        execute_query(query, (self.nombre, self.peso, self.opcional, self.evaluacion_id, self.topico_id, self.id))

    @classmethod
    def eliminar(cls, id):
        """Elimina una instancia de tópico"""
        query = "DELETE FROM instancias_topico WHERE id = %s"
        execute_query(query, (id,))

    def obtener_peso_de_evaluacion(self):
        """Obtiene el peso de la evaluación asociada"""
        if not self.evaluacion_id:
            return 0.0
        
        query = "SELECT porcentaje FROM evaluaciones WHERE id = %s"
        resultado = execute_query(query, (self.evaluacion_id,))
        return float(resultado[0][0]) if resultado else 0.0
