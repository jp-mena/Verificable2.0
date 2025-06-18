from sga.db.database import execute_query

class Horario:
    @staticmethod
    def insertar(seccion_id, bloque_id, sala_id):
        execute_query(
            "INSERT INTO horarios (seccion_id, bloque_id, sala_id) VALUES (%s,%s,%s)",
            (seccion_id, bloque_id, sala_id),
        )

    @staticmethod
    def vaciar_todos():
        execute_query("DELETE FROM horarios")

    @staticmethod
    def vaciar_semestre(semestre: int, anio: int):
        execute_query(
            """
            DELETE FROM horarios
            WHERE seccion_id IN (
                SELECT s.id
                FROM secciones s
                JOIN instancias_curso ic ON ic.id = s.instancia_id
                WHERE ic.semestre = %s AND ic.anio = %s
            )
            """,
            (semestre, anio),
        )
