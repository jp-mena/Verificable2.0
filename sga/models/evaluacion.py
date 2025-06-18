# filepath: models/evaluacion.py
from sga.db.database import execute_query
from sga.utils.validators import ValidationError, validate_required_string, safe_int_conversion

class Evaluacion:
    def __init__(self, id=None, nombre=None, porcentaje=None, seccion_id=None):
        self.id = id
        self.nombre = validate_required_string(nombre, "nombre") if nombre else None
        self.porcentaje = self._validate_porcentaje(porcentaje) if porcentaje is not None else None
        self.seccion_id = seccion_id
    
    def _validate_porcentaje(self, porcentaje):
        """Valida que el porcentaje esté en el rango correcto"""
        if porcentaje is None:            raise ValidationError("El porcentaje es requerido")
        
        try:
            porcentaje_float = float(porcentaje)
            if porcentaje_float <= 0:
                raise ValidationError("El porcentaje debe ser mayor que 0")
            if porcentaje_float > 100:
                raise ValidationError("El porcentaje no puede ser mayor que 100")
            return round(porcentaje_float, 2)  # Redondear a 2 decimales
        except (ValueError, TypeError):
            raise ValidationError("El porcentaje debe ser un número válido")
    
    @classmethod
    def crear(cls, nombre, porcentaje, seccion_id):
        """Crea una nueva evaluación"""
        try:
            # Validar ID de sección
            seccion_id = safe_int_conversion(seccion_id)
            if seccion_id is None or seccion_id <= 0:
                raise ValidationError("ID de sección debe ser un entero positivo")
            
            # Crear objeto para validar
            evaluacion = cls(None, nombre, porcentaje, seccion_id)
            
            # Verificar que la suma de porcentajes no exceda 100%
            cls._validar_suma_porcentajes(seccion_id, evaluacion.porcentaje)
            
            query = "INSERT INTO evaluaciones (nombre, porcentaje, seccion_id) VALUES (%s, %s, %s)"
            id_evaluacion = execute_query(query, (evaluacion.nombre, evaluacion.porcentaje, seccion_id))
            evaluacion.id = id_evaluacion
            return evaluacion
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al crear evaluación: {str(e)}")
    
    @classmethod
    def _validar_suma_porcentajes(cls, seccion_id, nuevo_porcentaje):
        """Valida que la suma de porcentajes no exceda 100%"""
        try:
            query = "SELECT SUM(porcentaje) FROM evaluaciones WHERE seccion_id = %s"
            resultado = execute_query(query, (seccion_id,))
            suma_actual = resultado[0][0] if resultado[0][0] else 0
            
            suma_total = suma_actual + nuevo_porcentaje
            if suma_total > 100:
                raise ValidationError(f"La suma de porcentajes ({suma_total:.2f}%) excedería el 100%. Suma actual: {suma_actual:.2f}%")
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al validar suma de porcentajes: {str(e)}")

    @classmethod
    def obtener_todos(cls):
        """Obtiene todas las evaluaciones"""
        query = """
        SELECT e.id, e.nombre, e.porcentaje, e.seccion_id, s.numero, 
               ic.semestre, ic.anio, c.codigo, c.nombre, ic.cerrado
        FROM evaluaciones e
        JOIN secciones s ON e.seccion_id = s.id
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        ORDER BY ic.anio DESC, ic.semestre DESC, s.numero, e.nombre
        """
        resultados = execute_query(query)
        return [
            {
                'id': fila[0],
                'nombre': fila[1],
                'porcentaje': fila[2],
                'seccion_id': fila[3],
                'seccion_numero': fila[4],
                'semestre': fila[5],
                'anio': fila[6],
                'curso_codigo': fila[7],
                'curso_nombre': fila[8],
                'curso_cerrado': bool(fila[9])
            }
            for fila in resultados
        ]

    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene una evaluación por ID"""
        query = "SELECT id, nombre, porcentaje, seccion_id FROM evaluaciones WHERE id = %s"
        resultado = execute_query(query, (id,))
        if resultado:
            fila = resultado[0]
            return cls(fila[0], fila[1], fila[2], fila[3])
        return None

    @classmethod
    def obtener_por_seccion(cls, seccion_id):
        """Obtiene todas las evaluaciones de una sección"""
        query = "SELECT id, nombre, porcentaje, seccion_id FROM evaluaciones WHERE seccion_id = %s"
        resultados = execute_query(query, (seccion_id,))
        return [cls(fila[0], fila[1], fila[2], fila[3]) for fila in resultados]

    def actualizar(self):
        """Actualiza la evaluación"""
        query = "UPDATE evaluaciones SET nombre = %s, porcentaje = %s, seccion_id = %s WHERE id = %s"
        execute_query(query, (self.nombre, self.porcentaje, self.seccion_id, self.id))

    @classmethod
    def eliminar(cls, id):
        """Elimina una evaluación"""
        query = "DELETE FROM evaluaciones WHERE id = %s"
        execute_query(query, (id,))
