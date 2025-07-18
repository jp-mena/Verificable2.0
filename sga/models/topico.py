from sga.db.database import execute_query
from sga.utils.validators import ValidationError, parse_integer_field, validate_required_string

class Topico:
    def __init__(self, id=None, nombre=None, tipo=None):
        self.id = parse_integer_field(id) if id is not None else None
        self.nombre = validate_required_string(nombre, "nombre") if nombre else None
        if tipo:
            self.tipo = self._validate_tipo(tipo)
        else:
            self.tipo = None
            
    def _validate_tipo(self, tipo):
        tipo = validate_required_string(tipo, "tipo")
        tipos_validos = [
            'control', 'tarea', 'actividad', 'proyecto', 'examen', 'quiz',
            'laboratorio', 'practica', 'ensayo', 'presentacion', 'seminario',
            'informe', 'investigacion', 'parcial', 'final'
        ]
        if tipo.lower() not in tipos_validos:
            raise ValidationError(f"Tipo debe ser uno de: {', '.join(tipos_validos)}")
        return tipo.lower()

    @classmethod
    def crear(cls, nombre, tipo):
        try:
            topico = cls(None, nombre, tipo)
            query = "INSERT INTO topicos (nombre, tipo) VALUES (%s, %s)"
            id_topico = execute_query(query, (topico.nombre, topico.tipo))
            topico.id = id_topico
            return topico
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al crear tópico: {str(e)}")

    @classmethod
    def obtener_todos(cls):
        try:
            query = "SELECT id, nombre, tipo FROM topicos ORDER BY tipo, nombre"
            resultados = execute_query(query)
            return [
                {
                    'id': fila[0],
                    'nombre': fila[1],
                    'tipo': fila[2]
                }
                for fila in resultados
            ]
        except Exception as e:
            raise ValidationError(f"Error al obtener todos los tópicos: {str(e)}")

    @classmethod
    def obtener_por_id(cls, id):
        try:
            id = parse_integer_field(id)
            if id is None or id <= 0:
                raise ValidationError("ID de tópico debe ser un entero positivo")
            
            query = "SELECT id, nombre, tipo FROM topicos WHERE id = %s"
            resultado = execute_query(query, (id,))
            if resultado:
                fila = resultado[0]
                return cls(fila[0], fila[1], fila[2])
            return None
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al obtener tópico por ID: {str(e)}")    
    @classmethod
    def obtener_por_nombre(cls, nombre):
        try:
            query = "SELECT id, nombre, tipo FROM topicos WHERE nombre = %s"
            resultado = execute_query(query, (nombre,))
            if resultado:
                fila = resultado[0]
                topico = cls(fila[0], fila[1], fila[2])
                return topico
            return None
        except Exception as e:
            print(f"Error obteniendo tópico por nombre: {e}")
            return None

    def actualizar(self):
        try:
            if self.id is None or self.id <= 0:
                raise ValidationError("ID de tópico no válido para actualización")
            if not self.nombre:
                raise ValidationError("Nombre es requerido para actualización")
            if not self.tipo:
                raise ValidationError("Tipo es requerido para actualización")
            
            query = "UPDATE topicos SET nombre = %s, tipo = %s WHERE id = %s"
            execute_query(query, (self.nombre, self.tipo, self.id))
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al actualizar tópico: {str(e)}")

    @classmethod
    def eliminar(cls, id):
        try:
            id = parse_integer_field(id)
            if id is None or id <= 0:
                raise ValidationError("ID de tópico debe ser un entero positivo")
            
            existing = cls.obtener_por_id(id)
            if not existing:
                raise ValidationError("Tópico no encontrado")
            
            query = "DELETE FROM topicos WHERE id = %s"
            execute_query(query, (id,))
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al eliminar tópico: {str(e)}")
    
    @staticmethod
    def update(topico_id, nombre, tipo):
        try:
            topico = Topico.obtener_por_id(topico_id)
            if not topico:
                raise ValidationError("Tópico no encontrado")
            
            topico.nombre = validate_required_string(nombre, "nombre")
            topico.tipo = topico._validate_tipo(tipo)
            topico.actualizar()
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al actualizar tópico: {str(e)}")
