# filepath: models/nota.py
from sga.db.database import execute_query
from sga.utils.validators import ValidationError, validate_float_range, safe_int_conversion

class Nota:
    def __init__(self, id=None, alumno_id=None, instancia_topico_id=None, nota=None):
        self.id = id
        self.alumno_id = alumno_id
        self.instancia_topico_id = instancia_topico_id
        self.nota = self._validate_nota(nota) if nota is not None else None
    
    def _validate_nota(self, nota):
        """Valida que la nota esté en el rango correcto"""
        if nota is None:
            raise ValidationError("La nota es requerida")
        
        # Validar rango de nota (1.0 a 7.0)
        validated_nota = validate_float_range(nota, 1.0, 7.0, "Nota")
          # Redondear a 1 decimal para evitar problemas de precisión
        return round(validated_nota, 1)
    
    @classmethod
    def existe_nota(cls, alumno_id, instancia_topico_id):
        """Verifica si ya existe una nota para un alumno en una instancia de tópico"""
        query = "SELECT COUNT(*) FROM notas WHERE alumno_id = %s AND instancia_topico_id = %s"
        resultado = execute_query(query, (alumno_id, instancia_topico_id))
        return resultado[0][0] > 0
    
    @classmethod
    def _verificar_alumno_inscrito(cls, alumno_id, instancia_topico_id):
        """Verifica que el alumno esté inscrito en el curso de la instancia de tópico"""
        try:
            query = """
            SELECT COUNT(*) FROM inscripciones i
            JOIN instancias_topico it ON it.id = %s
            JOIN evaluaciones e ON it.evaluacion_id = e.id
            JOIN secciones s ON e.seccion_id = s.id
            WHERE i.alumno_id = %s AND i.instancia_curso_id = s.instancia_id
            """
            resultado = execute_query(query, (instancia_topico_id, alumno_id))
            return resultado[0][0] > 0
        except Exception:
            return False

    @classmethod
    def crear(cls, alumno_id, instancia_topico_id, nota):
        """Crea una nueva nota después de validar que no existe duplicado"""
        try:
            # Validar IDs
            alumno_id = safe_int_conversion(alumno_id)
            instancia_topico_id = safe_int_conversion(instancia_topico_id)
            
            if alumno_id is None or alumno_id <= 0:
                raise ValidationError("ID de alumno debe ser un entero positivo")
            if instancia_topico_id is None or instancia_topico_id <= 0:
                raise ValidationError("ID de instancia de tópico debe ser un entero positivo")
                
            # Crear instancia para validar la nota
            nota_obj = cls(None, alumno_id, instancia_topico_id, nota)
            
            # Verificar si ya existe una nota
            if cls.existe_nota(alumno_id, instancia_topico_id):
                raise ValidationError("Ya existe una nota para este alumno en esta evaluación")
            
            # Verificar que el alumno esté inscrito en el curso
            if not cls._verificar_alumno_inscrito(alumno_id, instancia_topico_id):
                raise ValidationError("El alumno no está inscrito en este curso")
            
            query = "INSERT INTO notas (alumno_id, instancia_topico_id, nota) VALUES (%s, %s, %s)"
            id_nota = execute_query(query, (alumno_id, instancia_topico_id, nota_obj.nota))
            nota_obj.id = id_nota
            return nota_obj
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al crear nota: {str(e)}")

    @classmethod
    def obtener_todos(cls):
        """Obtiene todas las notas"""
        query = """
        SELECT n.id, n.alumno_id, n.instancia_topico_id, n.nota,
               a.nombre as alumno_nombre, a.correo as alumno_correo,
               it.nombre as instancia_nombre, it.peso,
               e.nombre as evaluacion_nombre, t.nombre as topico_nombre,
               s.numero, ic.semestre, ic.anio, c.codigo, ic.cerrado
        FROM notas n
        JOIN alumnos a ON n.alumno_id = a.id
        JOIN instancias_topico it ON n.instancia_topico_id = it.id
        JOIN evaluaciones e ON it.evaluacion_id = e.id
        JOIN topicos t ON it.topico_id = t.id
        JOIN secciones s ON e.seccion_id = s.id
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        ORDER BY ic.anio DESC, ic.semestre DESC, s.numero, a.nombre, e.nombre
        """
        resultados = execute_query(query)
        return [
            {
                'id': fila[0],
                'alumno_id': fila[1],
                'instancia_topico_id': fila[2],
                'nota': fila[3],
                'alumno_nombre': fila[4],
                'alumno_correo': fila[5],
                'instancia_nombre': fila[6],
                'peso': fila[7],
                'evaluacion_nombre': fila[8],
                'topico_nombre': fila[9],
                'seccion_numero': fila[10],
                'semestre': fila[11],
                'anio': fila[12],
                'curso_codigo': fila[13],
                'curso_cerrado': bool(fila[14]) if fila[14] is not None else False
            }
            for fila in resultados
        ]

    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene una nota por ID"""
        query = "SELECT id, alumno_id, instancia_topico_id, nota FROM notas WHERE id = %s"
        resultado = execute_query(query, (id,))
        if resultado:
            fila = resultado[0]
            return cls(fila[0], fila[1], fila[2], fila[3])
        return None

    @classmethod
    def obtener_por_alumno(cls, alumno_id):
        """Obtiene todas las notas de un alumno"""
        query = "SELECT id, alumno_id, instancia_topico_id, nota FROM notas WHERE alumno_id = %s"
        resultados = execute_query(query, (alumno_id,))
        return [cls(fila[0], fila[1], fila[2], fila[3]) for fila in resultados]

    def actualizar(self):
        """Actualiza la nota"""
        query = "UPDATE notas SET alumno_id = %s, instancia_topico_id = %s, nota = %s WHERE id = %s"
        execute_query(query, (self.alumno_id, self.instancia_topico_id, self.nota, self.id))

    @classmethod
    def eliminar(cls, id):
        """Elimina una nota"""
        query = "DELETE FROM notas WHERE id = %s"
        execute_query(query, (id,))
