from sga.db.database import execute_query
from sga.utils.validators import ValidationError, safe_int_conversion
from datetime import datetime

class InstanciaCurso:
    def __init__(self, id=None, semestre=None, anio=None, curso_id=None, cerrado=False):
        self.id = id
        self.semestre = self._validate_semestre(semestre) if semestre is not None else None
        self.anio = self._validate_anio(anio) if anio is not None else None
        self.curso_id = curso_id
        self.cerrado = cerrado
    
    def _validate_semestre(self, semestre):
        try:
            semestre_int = int(semestre)
            if semestre_int not in [1, 2]:
                raise ValidationError("El semestre debe ser 1 o 2")
            return semestre_int
        except (ValueError, TypeError):
            raise ValidationError("El semestre debe ser un número válido")
    
    def _validate_anio(self, anio):
        try:
            anio_int = int(anio)
            anio_actual = datetime.now().year
            if anio_int < 2000 or anio_int > anio_actual + 5:
                raise ValidationError(f"El año debe estar entre 2000 y {anio_actual + 5}")
            return anio_int
        except (ValueError, TypeError):
            raise ValidationError("El año debe ser un número válido")

    @classmethod
    def crear(cls, semestre, anio, curso_id):
        try:
            query = "INSERT INTO instancias_curso (semestre, anio, curso_id) VALUES (%s, %s, %s)"
            id_instancia = execute_query(query, (semestre, anio, curso_id))
            return cls(id_instancia, semestre, anio, curso_id)
        except Exception as e:
            raise ValidationError(f"Error al crear la instancia de curso: {str(e)}")

    @classmethod
    def obtener_todos(cls):
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
        try:
            if not id:
                return None
            
            query = """
            SELECT ic.id, ic.semestre, ic.anio, ic.curso_id, ic.cerrado, ic.fecha_cierre,
                   c.codigo, c.nombre
            FROM instancias_curso ic
            JOIN cursos c ON ic.curso_id = c.id
            WHERE ic.id = %s
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
        try:
            if not self.id:
                raise ValidationError("No se puede actualizar una instancia sin ID")
            
            query = "UPDATE instancias_curso SET semestre = %s, anio = %s, curso_id = %s WHERE id = %s"
            execute_query(query, (self.semestre, self.anio, self.curso_id, self.id))
        except Exception as e:            raise ValidationError(f"Error al actualizar la instancia de curso: {str(e)}")
    
    @classmethod
    def eliminar(cls, id):
        try:
            if not id:
                raise ValidationError("ID de instancia requerido")
            
            query = "DELETE FROM instancias_curso WHERE id = %s"
            execute_query(query, (id,))
        except Exception as e:
            raise ValidationError(f"Error al eliminar la instancia de curso: {str(e)}")

    def esta_cerrado(self):
        return getattr(self, 'cerrado', False)

    @classmethod
    def obtener_nota_final_alumno(cls, instancia_id, alumno_id):
        try:
            if not instancia_id or not alumno_id:
                return None
            
            query = """
            SELECT nota_final, fecha_calculo
            FROM notas_finales
            WHERE instancia_curso_id = %s AND alumno_id = %s
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
        try:
            instancia_id = safe_int_conversion(instancia_id)
            if instancia_id is None or instancia_id <= 0:
                raise ValidationError("ID de instancia debe ser un entero positivo")
            
            instancia = cls.obtener_por_id(instancia_id)
            if not instancia:
                raise ValidationError("La instancia de curso no existe")
            
            if instancia.esta_cerrado():
                raise ValidationError("El curso ya está cerrado")
            
            if not cls._verificar_notas_completas(instancia_id):
                raise ValidationError("No se puede cerrar el curso: faltan notas por asignar")
            
            if not cls._verificar_porcentajes_completos(instancia_id):
                raise ValidationError("No se puede cerrar el curso: la suma de porcentajes de evaluaciones no es 100%")
            
            cls._calcular_notas_finales(instancia_id)
            
            query = "UPDATE instancias_curso SET cerrado = 1, fecha_cierre = %s WHERE id = %s"
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            execute_query(query, (fecha_actual, instancia_id))
            
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al cerrar curso: {str(e)}")
    
    @classmethod
    def _verificar_notas_completas(cls, instancia_id):
        try:
            query = """
            SELECT COUNT(*) as faltantes FROM (
                SELECT i.alumno_id, it.id as instancia_topico_id
                FROM inscripciones i
                JOIN secciones s ON i.instancia_curso_id = s.instancia_id
                JOIN evaluaciones e ON s.id = e.seccion_id
                JOIN instancias_topico it ON e.id = it.evaluacion_id
                WHERE i.instancia_curso_id = %s
                EXCEPT
                SELECT n.alumno_id, n.instancia_topico_id
                FROM notas n
                JOIN instancias_topico it ON n.instancia_topico_id = it.id
                JOIN evaluaciones e ON it.evaluacion_id = e.id
                JOIN secciones s ON e.seccion_id = s.id
                WHERE s.instancia_id = %s
            ) as faltantes
            """
            resultado = execute_query(query, (instancia_id, instancia_id))
            return resultado[0][0] == 0
        except Exception:
            return False
    
    @classmethod
    def _verificar_porcentajes_completos(cls, instancia_id):
        try:
            query = """
            SELECT SUM(e.porcentaje) as suma_total
            FROM evaluaciones e
            JOIN secciones s ON e.seccion_id = s.id
            WHERE s.instancia_id = %s
            GROUP BY s.instancia_id
            """
            resultado = execute_query(query, (instancia_id,))
            if not resultado:
                return False
            suma_total = float(resultado[0][0] or 0)
            return abs(suma_total - 100.0) < 0.01  # Tolerar diferencias de redondeo
        except Exception:
            return False
    
    @classmethod
    def _calcular_notas_finales(cls, instancia_id):
        try:
            query_alumnos = """
            SELECT DISTINCT i.alumno_id, a.nombre
            FROM inscripciones i
            JOIN alumnos a ON i.alumno_id = a.id
            WHERE i.instancia_curso_id = %s
            """
            alumnos = execute_query(query_alumnos, (instancia_id,))
            
            for alumno_id, nombre in alumnos:
                query_notas = """
                SELECT n.nota, e.porcentaje
                FROM notas n
                JOIN instancias_topico it ON n.instancia_topico_id = it.id
                JOIN evaluaciones e ON it.evaluacion_id = e.id
                JOIN secciones s ON e.seccion_id = s.id                WHERE n.alumno_id = %s AND s.instancia_id = %s
                """
                notas_data = execute_query(query_notas, (alumno_id, instancia_id))
                
                if notas_data:
                    nota_final = sum(float(nota) * (float(porcentaje) / 100.0) for nota, porcentaje in notas_data)
                    nota_final = round(nota_final, 1)
                    query_final = """
                    INSERT INTO notas_finales (alumno_id, instancia_curso_id, nota_final) 
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE nota_final = %s
                    """
                    execute_query(query_final, (alumno_id, instancia_id, nota_final, nota_final))
        except Exception as e:
            raise ValidationError(f"Error al calcular notas finales: {str(e)}")
    
    @classmethod
    def obtener_alumnos_curso(cls, instancia_id):
        try:
            if not instancia_id:
                return []
            
            query = """
            SELECT a.id, a.nombre, a.correo, a.fecha_ingreso, i.fecha_inscripcion
            FROM alumnos a
            JOIN inscripciones i ON a.id = i.alumno_id
            WHERE i.instancia_curso_id = %s
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
            WHERE s.instancia_id = %s AND n.alumno_id = %s
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
                    'topico_tipo': fila[6]                }
                for fila in resultados
            ]
        except Exception as e:
            print(f"Error al obtener notas del alumno {alumno_id} en instancia {instancia_id}: {e}")
            return []

    @classmethod
    def calcular_nota_final_alumno(cls, instancia_id, alumno_id):
        try:
            if not instancia_id or not alumno_id:
                return 0.0
            
            query_evaluaciones = """
            SELECT DISTINCT e.id, e.porcentaje
            FROM evaluaciones e
            JOIN secciones s ON e.seccion_id = s.id
            WHERE s.instancia_id = %s
            """
            evaluaciones = execute_query(query_evaluaciones, (instancia_id,))
            
            if not evaluaciones:
                return 0.0
            
            nota_final = 0.0
            total_porcentaje = 0.0
            for evaluacion in evaluaciones:
                evaluacion_id = evaluacion[0]
                porcentaje_evaluacion = float(evaluacion[1] or 0)
                
                query_instancias = """
                SELECT it.peso, n.nota
                FROM instancias_topico it
                JOIN notas n ON n.instancia_topico_id = it.id
                WHERE it.evaluacion_id = %s AND n.alumno_id = %s
                """
                instancias = execute_query(query_instancias, (evaluacion_id, alumno_id))
                
                if instancias:
                    suma_ponderada = 0.0
                    suma_pesos = 0.0
                    
                    for instancia in instancias:
                        peso = float(instancia[0] or 0)
                        nota = float(instancia[1] or 0)
                        suma_ponderada += (nota * peso)
                        suma_pesos += peso
                    
                    if suma_pesos > 0:
                        promedio_evaluacion = suma_ponderada / suma_pesos
                        nota_final += (promedio_evaluacion * porcentaje_evaluacion / 100.0)                        
                        total_porcentaje += porcentaje_evaluacion
            
            if total_porcentaje > 0 and total_porcentaje != 100:
                nota_final = (nota_final * 100.0) / total_porcentaje
            
            return round(nota_final, 1)
            
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
            
            for alumno in alumnos:
                try:
                    alumno['notas'] = cls.obtener_notas_alumno_curso(instancia_id, alumno['id'])
                    
                    if instancia_dict['cerrado']:
                        nota_final_info = cls.obtener_nota_final_alumno(instancia_id, alumno['id'])
                        alumno['nota_final'] = nota_final_info
                    else:
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
