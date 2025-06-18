# sga/models/sala.py
from sga.db.database import execute_query
from sga.utils.validators import ValidationError, safe_int_conversion, validate_required_string

class Sala:
    def __init__(self, nombre, capacidad, id=None):
        self.id = id
        self.nombre = validate_required_string(nombre, "nombre")
        self.capacidad = safe_int_conversion(capacidad)

    @classmethod
    def crear(cls, nombre, capacidad):
        query = "INSERT INTO salas (nombre, capacidad) VALUES (?, ?)"
        sala_id = execute_query(query, (nombre, capacidad))
        return cls(nombre, capacidad, sala_id)

    @staticmethod
    def obtener_todas():
        return execute_query("SELECT id, nombre, capacidad FROM salas")

    @staticmethod
    def eliminar(id_):
        execute_query("DELETE FROM salas WHERE id = ?", (id_,))
