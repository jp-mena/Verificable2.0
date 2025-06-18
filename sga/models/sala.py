from sga.db.database import execute_query

class Sala:
    @staticmethod
    def obtener_todas():
        return execute_query("SELECT id, nombre, capacidad FROM salas")

    @staticmethod
    def obtener_por_id(sala_id: int):
        filas = execute_query(
            "SELECT id, nombre, capacidad FROM salas WHERE id=%s",
            (sala_id,)
        )
        return filas[0] if filas else None          # (id,nombre,capacidad) | None

    @staticmethod
    def crear(nombre: str, capacidad: int):
        execute_query(
            "INSERT INTO salas (nombre, capacidad) VALUES (%s, %s)",
            (nombre, capacidad)
        )

    @staticmethod
    def actualizar(sala_id: int, nombre: str, capacidad: int):
        execute_query(
            "UPDATE salas SET nombre=%s, capacidad=%s WHERE id=%s",
            (nombre, capacidad, sala_id)
        )

    @staticmethod
    def eliminar(sala_id: int):
        execute_query("DELETE FROM salas WHERE id=%s", (sala_id,))