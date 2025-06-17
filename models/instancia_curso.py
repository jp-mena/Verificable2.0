# filepath: models/instancia_curso.py
from db.database import execute_query
from utils.validators import ValidationError

class InstanciaCurso:
    def __init__(self, id=None, semestre=None, anio=None, curso_id=None):
        self.id = id
        self.semestre = semestre
        self.anio = anio
        self.curso_id = curso_id

    @classmethod
    def crear(cls, semestre, anio, curso_id):
        """Crea una nueva instancia de curso"""
        try:
            query = "INSERT INTO instancias_curso (semestre, anio, curso_id) VALUES (?, ?, ?)"
            id_instancia = execute_query(query, (semestre, anio, curso_id))
            return cls(id_instancia, semestre, anio, curso_id)
        except Exception as e:
            raise ValidationError(f"Error al crear la instancia de curso: {str(e)}")

    @classmethod
    def obtener_todos(cls):
        """Obtiene todas las instancias de curso"""
        try:
            query = """
            SELECT ic.id, ic.semestre, ic.anio, ic.curso_id, c.codigo, c.nombre, 
                   ic.cerrado, ic.fecha_cierre
            FROM instancias_curso ic
            JOIN cursos c ON ic.curso_id = c.id
            ORDER BY ic.anio DESC, ic.semestre DESC
            """
            resultados = execute_query(query)
            return [
                {
                    'id': fila[0],
                    'semestre': fila[1], 
                    'anio': fila[2],
                    'curso_id': fila[3],
                    'curso_codigo': fila[4],
                    'curso_nombre': fila[5],
                    'cerrado': bool(fila[6]) if fila[6] is not None else False,
                    'fecha_cierre': fila[7]
                }
                for fila in resultados
            ]
        except Exception as e:
            print(f"Error al obtener instancias de curso: {e}")
            return []

    @classmethod
    def obtener_por_id(cls, id):
        """Obtiene una instancia de curso por ID"""
        try:
            if not id:
                return None
            
            query = """
            SELECT ic.id, ic.semestre, ic.anio, ic.curso_id, ic.cerrado, ic.fecha_cierre,
                   c.codigo, c.nombre
            FROM instancias_curso ic
            JOIN cursos c ON ic.curso_id = c.id
            WHERE ic.id = ?
            """
            resultado = execute_query(query, (id,))
            if resultado:
                fila = resultado[0]
                instancia = cls(fila[0], fila[1], fila[2], fila[3])
                instancia.cerrado = bool(fila[4]) if fila[4] is not None else False
                instancia.fecha_cierre = fila[5]
                instancia.curso_codigo = fila[6]
                instancia.curso_nombre = fila[7]
                return instancia
            return None
        except Exception as e:
            print(f"Error al obtener instancia de curso por ID {id}: {e}")
            return None

    def actualizar(self):
        """Actualiza la instancia de curso"""
        try:
            if not self.id:
                raise ValidationError("No se puede actualizar una instancia sin ID")
            
            query = "UPDATE instancias_curso SET semestre = ?, anio = ?, curso_id = ? WHERE id = ?"
            execute_query(query, (self.semestre, self.anio, self.curso_id, self.id))
        except Exception as e:
            raise ValidationError(f"Error al actualizar la instancia de curso: {str(e)}")

    @classmethod
    def eliminar(cls, id):
        """Elimina una instancia de curso"""
        try:
            if not id:
                raise ValidationError("ID de instancia requerido")
            
            query = "DELETE FROM instancias_curso WHERE id = ?"
            execute_query(query, (id,))
        except Exception as e:
            raise ValidationError(f"Error al eliminar la instancia de curso: {str(e)}")

    def esta_cerrado(self):
        """Verifica si la instancia de curso está cerrada"""
        return getattr(self, 'cerrado', False)    @classmethod
    def obtener_nota_final_alumno(cls, instancia_id, alumno_id):
        """Obtiene la nota final de un alumno en una instancia cerrada"""
        try:
            if not instancia_id or not alumno_id:
                return None
            
            query = """
            SELECT nota_final, fecha_calculo
            FROM notas_finales
            WHERE instancia_curso_id = ? AND alumno_id = ?
            """
            resultado = execute_query(query, (instancia_id, alumno_id))
            if resultado:
                return {
                    'nota_final': resultado[0][0],
                    'fecha_calculo': resultado[0][1]
                }
            return None
        except Exception as e:
            print(f"Error al obtener nota final del alumno {alumno_id} en instancia {instancia_id}: {e}")
            return None

    @classmethod
    def cerrar_curso(cls, instancia_id):
        """Cierra un curso y calcula las notas finales de todos los alumnos"""
        try:
            from datetime import datetime
            
            if not instancia_id:
                return False
            
            # Verificar que no esté ya cerrado
            instancia = cls.obtener_por_id(instancia_id)
            if not instancia or getattr(instancia, 'cerrado', False):
                return False
            
            # Obtener todos los alumnos inscritos en el curso
            alumnos = cls.obtener_alumnos_curso(instancia_id)
            
            # Calcular y guardar nota final para cada alumno
            for alumno in alumnos:
                try:
                    nota_final = cls.calcular_nota_final_alumno(instancia_id, alumno['id'])
                    
                    # Guardar nota final en la tabla notas_finales
                    query_nota = """
                    INSERT OR REPLACE INTO notas_finales (instancia_curso_id, alumno_id, nota_final, fecha_calculo)
                    VALUES (?, ?, ?, ?)
                    """
                    execute_query(query_nota, (instancia_id, alumno['id'], nota_final, datetime.now()))
                except Exception as e:
                    print(f"Error al calcular nota final para alumno {alumno['id']}: {e}")
                    continue
            
            # Marcar el curso como cerrado
            query_cerrar = """
            UPDATE instancias_curso 
            SET cerrado = 1, fecha_cierre = ?
            WHERE id = ?
            """
            execute_query(query_cerrar, (datetime.now(), instancia_id))        
            return True
            
        except Exception as e:
            print(f"Error al cerrar curso {instancia_id}: {e}")
            return False

    @classmethod
    def obtener_alumnos_curso(cls, instancia_id):
        """Obtiene todos los alumnos inscritos en un curso a través de la tabla inscripciones"""
        try:
            if not instancia_id:
                return []
            
            query = """
            SELECT a.id, a.nombre, a.correo, a.fecha_ingreso, i.fecha_inscripcion
            FROM alumnos a
            JOIN inscripciones i ON a.id = i.alumno_id
            WHERE i.instancia_curso_id = ?
            ORDER BY a.nombre
            """
            resultados = execute_query(query, (instancia_id,))
            return [
                {
                    'id': fila[0],
                    'nombre': fila[1],
                    'correo': fila[2],
                    'fecha_ingreso': fila[3],
                    'fecha_inscripcion': fila[4]
                }
                for fila in resultados
            ]
        except Exception as e:
            print(f"Error al obtener alumnos del curso {instancia_id}: {e}")
            return []

    @classmethod
    def obtener_notas_alumno_curso(cls, instancia_id, alumno_id):
        """Obtiene todas las notas de un alumno en un curso específico"""
        try:
            if not instancia_id or not alumno_id:
                return []
            
            query = """
            SELECT 
                it.nombre as instancia_topico,
                n.nota,
                it.peso as peso_topico,
                e.nombre as evaluacion,
                e.porcentaje as peso_evaluacion,
                t.nombre as topico_nombre,
                t.tipo as topico_tipo
            FROM notas n
            JOIN instancias_topico it ON n.instancia_topico_id = it.id
            JOIN evaluaciones e ON it.evaluacion_id = e.id
            JOIN secciones s ON e.seccion_id = s.id
            JOIN topicos t ON it.topico_id = t.id
            WHERE s.instancia_id = ? AND n.alumno_id = ?
            ORDER BY e.nombre, it.nombre
            """
            resultados = execute_query(query, (instancia_id, alumno_id))
            return [
                {
                    'instancia_topico': fila[0],
                    'nota': fila[1],
                    'peso_topico': fila[2],
                    'evaluacion': fila[3],
                    'peso_evaluacion': fila[4],
                    'topico_nombre': fila[5],
                    'topico_tipo': fila[6]
                }
                for fila in resultados
            ]
        except Exception as e:
            print(f"Error al obtener notas del alumno {alumno_id} en instancia {instancia_id}: {e}")
            return []

    @classmethod
    def calcular_nota_final_alumno(cls, instancia_id, alumno_id):
        """Calcula la nota final de un alumno específico"""
        try:
            if not instancia_id or not alumno_id:
                return 0.0
            
            # Obtener todas las evaluaciones y sus ponderaciones
            query = """
            SELECT e.id, e.porcentaje, AVG(n.nota) as promedio_evaluacion
            FROM evaluaciones e
            JOIN secciones s ON e.seccion_id = s.id
            JOIN instancias_topico it ON it.evaluacion_id = e.id
            JOIN notas n ON n.instancia_topico_id = it.id
            WHERE s.instancia_id = ? AND n.alumno_id = ?
            GROUP BY e.id, e.porcentaje
            """
            evaluaciones = execute_query(query, (instancia_id, alumno_id))
            
            if not evaluaciones:
                return 0.0
            
            nota_final = 0.0
            total_porcentaje = 0.0
            
            for evaluacion in evaluaciones:
                porcentaje = evaluacion[1] or 0
                promedio = evaluacion[2] or 0
                
                nota_final += (promedio * porcentaje / 100.0)
                total_porcentaje += porcentaje
            
            # Normalizar si el total de porcentajes no es 100%
            if total_porcentaje > 0 and total_porcentaje != 100:
                nota_final = (nota_final * 100.0) / total_porcentaje
            
            return round(nota_final, 2)
            
        except Exception as e:
            print(f"Error al calcular nota final del alumno {alumno_id} en instancia {instancia_id}: {e}")
            return 0.0

    @classmethod
    def obtener_resumen_curso(cls, instancia_id):
        """Obtiene un resumen completo del curso con alumnos y notas"""
        try:
            if not instancia_id:
                return None
            
            instancia = cls.obtener_por_id(instancia_id)
            if not instancia:
                return None
            
            # Convertir instancia a diccionario para la plantilla
            instancia_dict = {
                'id': instancia.id,
                'semestre': instancia.semestre,
                'anio': instancia.anio,
                'curso_id': instancia.curso_id,
                'curso_codigo': getattr(instancia, 'curso_codigo', ''),
                'curso_nombre': getattr(instancia, 'curso_nombre', ''),
                'cerrado': getattr(instancia, 'cerrado', False),
                'fecha_cierre': getattr(instancia, 'fecha_cierre', None)
            }
            
            alumnos = cls.obtener_alumnos_curso(instancia_id)
            
            # Agregar notas a cada alumno
            for alumno in alumnos:
                try:
                    alumno['notas'] = cls.obtener_notas_alumno_curso(instancia_id, alumno['id'])
                    
                    # Si el curso está cerrado, obtener nota final
                    if instancia_dict['cerrado']:
                        nota_final_info = cls.obtener_nota_final_alumno(instancia_id, alumno['id'])
                        alumno['nota_final'] = nota_final_info
                    else:
                        # Si no está cerrado, calcular nota final temporal
                        alumno['nota_final_temporal'] = cls.calcular_nota_final_alumno(instancia_id, alumno['id'])
                except Exception as e:
                    print(f"Error al procesar datos del alumno {alumno['id']}: {e}")
                    alumno['notas'] = []
                    alumno['nota_final'] = None
                    alumno['nota_final_temporal'] = 0.0
            
            return {
                'instancia': instancia_dict,
                'alumnos': alumnos
            }
            
        except Exception as e:
            print(f"Error al obtener resumen del curso {instancia_id}: {e}")
            return None
