"""Modelo Horario
================
Encapsula operaciones CRUD mínimas sobre la tabla `horarios`.
Se usa exclusivamente desde SchedulerService y las vistas para leer la grilla.
"""
from sga.db.database import execute_query

class Horario:
    @staticmethod
    def insertar(seccion_id: int, bloque_id: int, sala_id: int) -> None:
        """Inserta una fila (id autoincremental) sin devolver resultado."""
        execute_query(
            "INSERT INTO horarios (seccion_id, bloque_id, sala_id) VALUES (%s,%s,%s)",
            (seccion_id, bloque_id, sala_id),
        )

    # ---------------------------------------------------------------------
    @staticmethod
    def vaciar_todos() -> None:
        """Elimina *todas* las filas (se usa al recalcular sin filtro)."""
        execute_query("DELETE FROM horarios")

    @staticmethod
    def vaciar_por_semestre(semestre: int, anio: int) -> None:
        """Elimina solo los horarios pertenencientes al período dado."""
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

    # ---------------------------------------------------------------------
    @staticmethod
    def obtener(join_extra: bool = True):
        """Retorna todas las filas. Si *join_extra* es True devuelve información
        enriquecida para la vista calendario (sigla, sala, hora,…)."""
        if not join_extra:
            return execute_query("SELECT * FROM horarios")

        qry = """
        SELECT c.codigo,
               s.numero,
               sal.nombre,
               b.dia,
               b.inicio,
               b.fin
        FROM horarios h
        JOIN secciones s       ON s.id  = h.seccion_id
        JOIN instancias_curso ic ON ic.id = s.instancia_id
        JOIN cursos c          ON c.id  = ic.curso_id
        JOIN bloques b         ON b.id  = h.bloque_id
        JOIN salas sal         ON sal.id = h.sala_id
        WHERE ic.semestre=%s AND ic.anio=%s
        """
        return execute_query(qry)
