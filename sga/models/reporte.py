from decimal import Decimal
from sga.db.database import execute_query
from sga.utils.validators import ValidationError, parse_integer_field

class Reporte:
    @classmethod
    def _obtener_datos_brutos_notas_instancia_topico(cls, instancia_topico_id):
        query = """
        SELECT 
            a.id as alumno_id,
            a.nombre as alumno_nombre,
            a.correo as alumno_correo,
            n.nota,
            it.nombre as instancia_topico_nombre,
            it.peso as peso_topico,
            e.nombre as evaluacion_nombre,
            e.porcentaje as porcentaje_evaluacion,
            t.nombre as topico_nombre,
            t.tipo as topico_tipo,
            s.numero as seccion_numero,
            c.codigo as curso_codigo,
            c.nombre as curso_nombre,
            ic.semestre,
            ic.anio,
            ic.cerrado
        FROM notas n        
        JOIN alumnos a ON n.alumno_id = a.id
        JOIN instancias_topico it ON n.instancia_topico_id = it.id
        JOIN evaluaciones e ON it.evaluacion_id = e.id
        JOIN topicos t ON it.topico_id = t.id
        JOIN secciones s ON e.seccion_id = s.id
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        WHERE it.id = %s
        ORDER BY a.nombre
        """
        return execute_query(query, (instancia_topico_id,))

    @classmethod
    def _mapear_fila_notas_instancia_topico(cls, fila):
        return {
            'alumno_id': fila[0],
            'alumno_nombre': fila[1],
            'alumno_correo': fila[2],
            'nota': fila[3],
            'instancia_topico_nombre': fila[4],
            'peso_topico': fila[5],
            'evaluacion_nombre': fila[6],
            'porcentaje_evaluacion': fila[7],
            'topico_nombre': fila[8],
            'topico_tipo': fila[9],
            'seccion_numero': fila[10],
            'curso_codigo': fila[11],
            'curso_nombre': fila[12],
            'semestre': fila[13],
            'anio': fila[14],
            'cerrado': bool(fila[15]) if fila[15] is not None else False
        }

    @classmethod
    def obtener_notas_instancia_topico(cls, instancia_topico_id):
        try:
            instancia_topico_id = parse_integer_field(instancia_topico_id)
            if instancia_topico_id is None or instancia_topico_id <= 0:
                raise ValidationError("ID de instancia de tópico debe ser un entero positivo")
            
            resultados = cls._obtener_datos_brutos_notas_instancia_topico(instancia_topico_id)
            return [cls._mapear_fila_notas_instancia_topico(fila) for fila in resultados]
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error en obtener_notas_instancia_topico: {str(e)}")
        
        
    @classmethod
    def _obtener_datos_brutos_notas_finales_seccion(cls, instancia_curso_id, seccion_numero):
        query = """
        SELECT 
            a.id as alumno_id,
            a.nombre as alumno_nombre,
            a.correo as alumno_correo,
            nf.nota_final,
            nf.fecha_calculo,
            c.codigo as curso_codigo,
            c.nombre as curso_nombre,
            ic.semestre,
            ic.anio,
            s.numero as seccion_numero,
            ic.cerrado,
            ic.fecha_cierre
        FROM notas_finales nf
        JOIN alumnos a ON nf.alumno_id = a.id
        JOIN instancias_curso ic ON nf.instancia_curso_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        JOIN inscripciones i ON i.alumno_id = a.id AND i.instancia_curso_id = ic.id
        LEFT JOIN secciones s ON s.instancia_id = ic.id AND s.numero = %s
        WHERE ic.id = %s 
        AND ic.cerrado = 1
        AND s.id IS NOT NULL
        ORDER BY a.nombre
        """
        return execute_query(query, (seccion_numero, instancia_curso_id))

    @classmethod
    def _mapear_fila_notas_finales_seccion(cls, fila):
        return {
            'alumno_id': fila[0],
            'alumno_nombre': fila[1],
            'alumno_correo': fila[2],
            'nota_final': fila[3],
            'fecha_calculo': fila[4],
            'curso_codigo': fila[5],
            'curso_nombre': fila[6],
            'semestre': fila[7],
            'anio': fila[8],
            'seccion_numero': fila[9],
            'cerrado': bool(fila[10]) if fila[10] is not None else False,
            'fecha_cierre': fila[11]
        }
    
    @classmethod
    def obtener_notas_finales_seccion(cls, instancia_curso_id, seccion_numero):
        try:
            instancia_curso_id = parse_integer_field(instancia_curso_id)
            seccion_numero = parse_integer_field(seccion_numero)
            
            if instancia_curso_id is None or instancia_curso_id <= 0:
                raise ValidationError("ID de instancia de curso debe ser un entero positivo")
            
            if seccion_numero is None or seccion_numero <= 0:
                raise ValidationError("Número de sección debe ser un entero positivo")
            
            resultados = cls._obtener_datos_brutos_notas_finales_seccion(instancia_curso_id, seccion_numero)
            return [cls._mapear_fila_notas_finales_seccion(fila) for fila in resultados]
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error en obtener_notas_finales_seccion: {str(e)}")
    @classmethod
    def _obtener_datos_brutos_certificado_notas_alumno(cls, alumno_id):
        query = """
        SELECT 
            nf.nota_final,
            c.codigo as curso_codigo,
            c.nombre as curso_nombre,
            ic.semestre,
            ic.anio,
            s.numero as seccion_numero,
            nf.fecha_calculo,
            ic.fecha_cierre,
            CASE 
                WHEN nf.nota_final >= 4.0 THEN 'Aprobado'
                ELSE 'Reprobado'
            END as estado
        FROM notas_finales nf
        JOIN instancias_curso ic ON nf.instancia_curso_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        JOIN secciones s ON s.instancia_id = ic.id
        WHERE nf.alumno_id = %s
        AND ic.cerrado = 1
        ORDER BY ic.anio DESC, ic.semestre DESC, c.codigo
        """
        return execute_query(query, (alumno_id,))

    @classmethod
    def _mapear_fila_certificado_notas_alumno(cls, fila):
        return {
            'nota_final': fila[0],
            'curso_codigo': fila[1],
            'curso_nombre': fila[2],
            'semestre': fila[3],
            'anio': fila[4],
            'seccion_numero': fila[5],
            'fecha_calculo': fila[6],
            'fecha_cierre': fila[7],
            'estado': fila[8]
        }

    @classmethod
    def obtener_certificado_notas_alumno(cls, alumno_id):
        try:
            alumno_id = parse_integer_field(alumno_id)
            if alumno_id is None or alumno_id <= 0:
                raise ValidationError("ID de alumno debe ser un entero positivo")
            
            resultados = cls._obtener_datos_brutos_certificado_notas_alumno(alumno_id)
            return [cls._mapear_fila_certificado_notas_alumno(fila) for fila in resultados]
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error en obtener_certificado_notas_alumno: {str(e)}")
    @classmethod
    def _obtener_datos_brutos_instancias_topico_disponibles(cls):
        query = """
        SELECT 
            it.id,
            it.nombre as instancia_nombre,
            e.nombre as evaluacion_nombre,
            t.nombre as topico_nombre,
            s.numero as seccion_numero,
            c.codigo as curso_codigo,
            c.nombre as curso_nombre,
            ic.semestre,
            ic.anio
        FROM instancias_topico it
        JOIN evaluaciones e ON it.evaluacion_id = e.id
        JOIN topicos t ON it.topico_id = t.id
        JOIN secciones s ON e.seccion_id = s.id
        JOIN instancias_curso ic ON s.instancia_id = ic.id
        JOIN cursos c ON ic.curso_id = c.id
        ORDER BY ic.anio DESC, ic.semestre DESC, c.codigo, s.numero, e.nombre, it.nombre
        """
        return execute_query(query)

    @classmethod
    def _mapear_fila_instancias_topico_disponibles(cls, fila):
        return {
            'id': fila[0],
            'instancia_nombre': fila[1],
            'evaluacion_nombre': fila[2],
            'topico_nombre': fila[3],
            'seccion_numero': fila[4],
            'curso_codigo': fila[5],
            'curso_nombre': fila[6],
            'semestre': fila[7],
            'anio': fila[8],
            'display_name': f"{fila[5]} {fila[8]}{fila[7]:02d} - Sec.{fila[4]} - {fila[2]} - {fila[1]}"
        }

    @classmethod
    def obtener_instancias_topico_disponibles(cls):
        try:
            resultados = cls._obtener_datos_brutos_instancias_topico_disponibles()
            return [cls._mapear_fila_instancias_topico_disponibles(fila) for fila in resultados]
        except Exception as e:
            raise ValidationError(f"Error en obtener_instancias_topico_disponibles: {str(e)}")
    @classmethod
    def _obtener_datos_brutos_cursos_cerrados(cls):
        query = """
        SELECT DISTINCT
            ic.id,
            c.codigo as curso_codigo,
            c.nombre as curso_nombre,
            ic.semestre,
            ic.anio,
            ic.fecha_cierre,
            COUNT(DISTINCT s.numero) as total_secciones
        FROM instancias_curso ic
        JOIN cursos c ON ic.curso_id = c.id
        JOIN secciones s ON s.instancia_id = ic.id
        WHERE ic.cerrado = 1
        GROUP BY ic.id, c.codigo, c.nombre, ic.semestre, ic.anio, ic.fecha_cierre
        ORDER BY ic.anio DESC, ic.semestre DESC, c.codigo
        """
        return execute_query(query)

    @classmethod
    def _mapear_fila_cursos_cerrados(cls, fila):
        return {
            'id': fila[0],
            'curso_codigo': fila[1],
            'curso_nombre': fila[2],
            'semestre': fila[3],
            'anio': fila[4],
            'fecha_cierre': fila[5],
            'total_secciones': fila[6],
            'display_name': f"{fila[1]} {fila[4]}{fila[3]:02d} - {fila[2]}"
        }

    @classmethod
    def obtener_cursos_cerrados(cls):
        try:
            resultados = cls._obtener_datos_brutos_cursos_cerrados()
            return [cls._mapear_fila_cursos_cerrados(fila) for fila in resultados]
        except Exception as e:
            raise ValidationError(f"Error en obtener_cursos_cerrados: {str(e)}")
    @classmethod
    def _obtener_datos_brutos_secciones_curso_cerrado(cls, instancia_curso_id):
        query = """
        SELECT DISTINCT
            s.numero,
            COUNT(DISTINCT nf.alumno_id) as total_alumnos
        FROM secciones s
        LEFT JOIN evaluaciones e ON e.seccion_id = s.id
        LEFT JOIN instancias_topico it ON it.evaluacion_id = e.id
        LEFT JOIN notas n ON n.instancia_topico_id = it.id
        LEFT JOIN notas_finales nf ON nf.alumno_id = n.alumno_id AND nf.instancia_curso_id = s.instancia_id
        WHERE s.instancia_id = %s
        GROUP BY s.numero
        ORDER BY s.numero
        """
        return execute_query(query, (instancia_curso_id,))

    @classmethod
    def _mapear_fila_secciones_curso_cerrado(cls, fila):
        return {
            'numero': fila[0],
            'total_alumnos': fila[1] or 0
        }

    @classmethod
    def obtener_secciones_curso_cerrado(cls, instancia_curso_id):
        try:
            instancia_curso_id = parse_integer_field(instancia_curso_id)
            if instancia_curso_id is None or instancia_curso_id <= 0:
                raise ValidationError("ID de instancia de curso debe ser un entero positivo")
            
            resultados = cls._obtener_datos_brutos_secciones_curso_cerrado(instancia_curso_id)
            return [cls._mapear_fila_secciones_curso_cerrado(fila) for fila in resultados]
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error en obtener_secciones_curso_cerrado: {str(e)}")
    @classmethod
    def _obtener_datos_brutos_alumnos_con_cursos_cerrados(cls):
        query = """
        SELECT DISTINCT
            a.id,
            a.nombre,
            a.correo,
            COUNT(DISTINCT nf.instancia_curso_id) as total_cursos_cerrados
        FROM alumnos a
        JOIN notas_finales nf ON a.id = nf.alumno_id
        JOIN instancias_curso ic ON nf.instancia_curso_id = ic.id
        WHERE ic.cerrado = 1
        GROUP BY a.id, a.nombre, a.correo
        ORDER BY a.nombre
        """        
        return execute_query(query)

    @classmethod
    def _mapear_fila_alumnos_con_cursos_cerrados(cls, fila):
        return {
            'id': fila[0],
            'nombre': fila[1],
            'correo': fila[2],
            'total_cursos_cerrados': fila[3],
            'display_name': f"{fila[1]} ({fila[2]}) - {fila[3]} curso(s) cerrado(s)"
        }

    @classmethod
    def obtener_alumnos_con_cursos_cerrados(cls):
        try:
            resultados = cls._obtener_datos_brutos_alumnos_con_cursos_cerrados()
            return [cls._mapear_fila_alumnos_con_cursos_cerrados(fila) for fila in resultados]
        except Exception as e:
            raise ValidationError(f"Error en obtener_alumnos_con_cursos_cerrados: {str(e)}")
    @classmethod
    def calcular_estadisticas_seccion(cls, notas):
        try:
            if not cls._validar_notas_input(notas):
                return cls._crear_estadisticas_vacias()
                
            notas_validas = cls._filtrar_notas_validas(notas)
            total_estudiantes = len(notas)
            
            if not notas_validas:
                return cls._crear_estadisticas_sin_notas(total_estudiantes)
            
            return cls._calcular_estadisticas_completas(notas_validas, total_estudiantes)
            
        except Exception as e:
            raise ValidationError(f"Error en calcular_estadisticas_seccion: {str(e)}")
    
    @classmethod
    def _validar_notas_input(cls, notas):
        return notas and isinstance(notas, list)
    
    @classmethod
    def _crear_estadisticas_vacias(cls):
        return {
            'total_estudiantes': 0,
            'promedio': None,
            'aprobados': 0,
            'reprobados': 0
        }
    
    @classmethod
    def _filtrar_notas_validas(cls, notas):
        return [
            n for n in notas 
            if n.get('nota_final') is not None 
            and isinstance(n.get('nota_final'), (int, float, Decimal))
        ]
    
    @classmethod
    def _crear_estadisticas_sin_notas(cls, total_estudiantes):
        return {
            'total_estudiantes': total_estudiantes,
            'promedio': None,
            'aprobados': 0,
            'reprobados': 0
        }
    
    @classmethod
    def _calcular_estadisticas_completas(cls, notas_validas, total_estudiantes):
        promedio = cls._calcular_promedio(notas_validas)
        aprobados, reprobados = cls._contar_aprobados_reprobados(notas_validas)
        
        return {
            'total_estudiantes': total_estudiantes,
            'promedio': round(promedio, 2),
            'aprobados': aprobados,
            'reprobados': reprobados
        }
    
    @classmethod
    def _calcular_promedio(cls, notas_validas):
        suma_notas = sum(float(n['nota_final']) for n in notas_validas)
        return suma_notas / len(notas_validas)
    
    @classmethod
    def _contar_aprobados_reprobados(cls, notas_validas):
        aprobados = len([n for n in notas_validas if float(n['nota_final']) >= 4.0])
        reprobados = len([n for n in notas_validas if float(n['nota_final']) < 4.0])
        return aprobados, reprobados
    
    @classmethod
    def calcular_estadisticas_alumno(cls, certificado):
        try:
            if not cls._validar_certificado_input(certificado):
                return cls._crear_estadisticas_alumno_vacias()
                
            notas_validas = cls._filtrar_notas_validas_alumno(certificado)
            total_cursos = len(certificado)
            
            if not notas_validas:
                return cls._crear_estadisticas_alumno_sin_notas(total_cursos)
            
            return cls._calcular_estadisticas_alumno_completas(certificado, notas_validas, total_cursos)
            
        except Exception as e:
            raise ValidationError(f"Error en calcular_estadisticas_alumno: {str(e)}")
    
    @classmethod
    def _validar_certificado_input(cls, certificado):
        return certificado and isinstance(certificado, list)
    
    @classmethod
    def _crear_estadisticas_alumno_vacias(cls):
        return {
            'total_cursos': 0,
            'promedio_general': None,
            'cursos_aprobados': 0,
            'cursos_reprobados': 0,
            'creditos_totales': 0
        }
    
    @classmethod
    def _filtrar_notas_validas_alumno(cls, certificado):
        return [
            c for c in certificado 
            if c.get('nota_final') is not None 
            and isinstance(c.get('nota_final'), (int, float))
        ]
    
    @classmethod
    def _crear_estadisticas_alumno_sin_notas(cls, total_cursos):
        return {
            'total_cursos': total_cursos,
            'promedio_general': None,
            'cursos_aprobados': 0,
            'cursos_reprobados': 0,
            'creditos_totales': 0
        }
    
    @classmethod
    def _calcular_estadisticas_alumno_completas(cls, certificado, notas_validas, total_cursos):
        promedio_general = cls._calcular_promedio_general(notas_validas)
        cursos_aprobados, cursos_reprobados = cls._contar_cursos_aprobados_reprobados(notas_validas)
        creditos_totales = cls._calcular_creditos_totales(certificado)
        
        return {
            'total_cursos': total_cursos,
            'promedio_general': round(promedio_general, 2),
            'cursos_aprobados': cursos_aprobados,
            'cursos_reprobados': cursos_reprobados,
            'creditos_totales': creditos_totales
        }
    
    @classmethod
    def _calcular_promedio_general(cls, notas_validas):
        suma_notas = sum(c['nota_final'] for c in notas_validas)
        return suma_notas / len(notas_validas)
    
    @classmethod
    def _contar_cursos_aprobados_reprobados(cls, notas_validas):
        cursos_aprobados = len([c for c in notas_validas if c['nota_final'] >= 4.0])
        cursos_reprobados = len([c for c in notas_validas if c['nota_final'] < 4.0])
        return cursos_aprobados, cursos_reprobados
    
    @classmethod
    def _calcular_creditos_totales(cls, certificado):
        return sum(parse_integer_field(c.get('creditos', 0)) or 0 for c in certificado)
