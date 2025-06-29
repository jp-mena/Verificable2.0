import re
from datetime import datetime
from sga.db.database import execute_query
from sga.utils.validators import (
    ValidationError, parse_integer_field, validate_required_string
)


TIME_FMT = "%H:%M"
TIME_RE  = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


class Bloque:
    def __init__(self, dia, inicio, fin, id=None):
        self.dia    = parse_integer_field(dia)
        if not 1 <= self.dia <= 6:
            raise ValidationError("El campo 'dia' debe ser 1-6 (lun-sáb).")

        self.inicio = self._parse_time(inicio, "inicio")
        self.fin    = self._parse_time(fin,    "fin")
        if self.inicio >= self.fin:
            raise ValidationError("'inicio' debe ser antes que 'fin'.")

        self.id = id

    @classmethod
    def crear(cls, dia, inicio, fin):
        nuevo = cls(dia, inicio, fin)
        bloque_id = execute_query(
            "INSERT INTO bloques (dia, inicio, fin) VALUES (?, ?, ?)",
            (nuevo.dia, nuevo.inicio, nuevo.fin)
        )
        nuevo.id = bloque_id
        return nuevo

    @staticmethod
    def obtener_todos():
        return execute_query(
            "SELECT id, dia, inicio, fin FROM bloques ORDER BY dia, inicio"
        )

    @staticmethod
    def eliminar(id_):
        execute_query("DELETE FROM bloques WHERE id = ?", (id_,))

    @staticmethod
    def _parse_time(value, field):
        if not value or not isinstance(value, str):
            raise ValidationError(f"'{field}' es obligatorio")

        if not TIME_RE.fullmatch(value.strip()):
            raise ValidationError(f"'{field}' debe tener formato HH:MM (24 h)")

        return value.strip()
