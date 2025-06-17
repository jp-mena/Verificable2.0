# filepath: models/seccion.py
from sga.db.database import execute_query

class Seccion:
    def __init__(self, id=None, numero=None, instancia_id=None, profesor_id=None):
        self.id = id
        self.numero = numero
        self.instancia_id = instancia_id
        self.profesor_id = profesor_id

    @classmethod
    def crear(cls, numero, instancia_id, profesor_id=None):
        """Crea una nueva sección"""
        query = "INSERT INTO secciones (numero, instancia_id, profesor_id) VALUES (?, ?, ?)"
        id_seccion = execute_query(query, (numero, instancia_id, profesor_id))
        return cls(id_seccion, numero, instancia_id, profesor_id)

    @classmethod
    def obtener_todos(cls):
        """Obtiene todas las secciones"""
        query = """
        SELECT s.id, s.numero, s.instancia_id, s.profesor_id,
               ic.semestre, ic.anio, c.codigo, c.nombre, ic.cerrado,
               p.nombre as profesor_nombre
        FROM secciones s
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        LEFT JOIN profesores p ON s.profesor_id = p.id
        ORDER BY ic.anio DESC, ic.semestre DESC, s.numero
        """
        resultados = execute_query(query)
        return [
            {
                'id': fila[0],
                'numero': fila[1],
                'instancia_id': fila[2],
                'profesor_id': fila[3],
                'semestre': fila[4],
                'anio': fila[5],
                'curso_codigo': fila[6],
                'curso_nombre': fila[7],
                'curso_cerrado': bool(fila[8]),
                'profesor_nombre': fila[9] if fila[9] else 'Sin asignar'
            }
            for fila in resultados
        ]

    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene una sección por ID"""
        query = "SELECT id, numero, instancia_id, profesor_id FROM secciones WHERE id = ?"
        resultado = execute_query(query, (id,))
        if resultado:
            fila = resultado[0]
            return cls(fila[0], fila[1], fila[2], fila[3])
        return None

    def actualizar(self):
        """Actualiza la sección"""
        query = "UPDATE secciones SET numero = ?, instancia_id = ?, profesor_id = ? WHERE id = ?"
        execute_query(query, (self.numero, self.instancia_id, self.profesor_id, self.id))
        return True    @staticmethod
    def eliminar(id):
        """Elimina una sección"""
        query = "DELETE FROM secciones WHERE id = ?"
        execute_query(query, (id,))

    @staticmethod
    def obtener_profesores_disponibles(instancia_id, seccion_id_actual=None):
        """
        Obtiene todos los profesores EXCEPTO los que ya están asignados 
        a otras secciones de la MISMA instancia específica
        """
        try:
            # Obtener todos los profesores
            from sga.models.profesor import Profesor
            todos_profesores = Profesor.get_all()
            
            # Obtener profesores ya asignados a otras secciones de ESTA MISMA instancia
            query = """
            SELECT DISTINCT profesor_id 
            FROM secciones 
            WHERE instancia_id = ? AND profesor_id IS NOT NULL
            """
            params = [instancia_id]
            
            # Si estamos editando una sección, excluir esa sección del filtro
            if seccion_id_actual:
                query += " AND id != ?"
                params.append(seccion_id_actual)
            
            profesores_ocupados_en_esta_instancia = execute_query(query, params)
            ids_ocupados = [prof[0] for prof in profesores_ocupados_en_esta_instancia]
            
            # Filtrar profesores: mostrar todos EXCEPTO los ya asignados a esta instancia
            profesores_disponibles = []
            for profesor in todos_profesores:
                if profesor[0] not in ids_ocupados:  # profesor[0] es el ID
                    profesores_disponibles.append({
                        'id': profesor[0],
                        'nombre': profesor[1],
                        'correo': profesor[2]
                    })
            
            return profesores_disponibles
            
        except Exception as e:
            print(f"Error en obtener_profesores_disponibles: {e}")
            return []
