# filepath: models/reporte.py
from db.database import execute_query

class Reporte:
    
    @classmethod
    def obtener_notas_instancia_topico(cls, instancia_topico_id):
        """
        Reporte a: Notas de una cierta instancia de tópico
        Ejemplo: notas de la entrega 2 del proyecto, de la sección 1 del curso ICC5130 202501
        """
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
        WHERE it.id = ?
        ORDER BY a.nombre
        """
        resultados = execute_query(query, (instancia_topico_id,))
        return [
            {
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
            for fila in resultados
        ]
    
    @classmethod
    def obtener_notas_finales_seccion(cls, instancia_curso_id, seccion_numero):
        """
        Reporte b: Notas finales de una sección de un curso cerrado
        Ejemplo: notas finales de la sección 1 de ICC5130 202501
        """
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
        JOIN secciones s ON s.instancia_id = ic.id
        WHERE ic.id = ? 
        AND s.numero = ?
        AND ic.cerrado = 1
        ORDER BY a.nombre
        """
        resultados = execute_query(query, (instancia_curso_id, seccion_numero))
        return [
            {
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
            for fila in resultados
        ]
    
    @classmethod
    def obtener_certificado_notas_alumno(cls, alumno_id):
        """
        Reporte c: Certificado de notas - todas las notas finales de cursos cerrados de un alumno
        Muestra: nota final, curso, instancia, sección, fecha (año/semestre)
        """
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
        WHERE nf.alumno_id = ?
        AND ic.cerrado = 1
        ORDER BY ic.anio DESC, ic.semestre DESC, c.codigo
        """
        resultados = execute_query(query, (alumno_id,))
        return [
            {
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
            for fila in resultados
        ]
    
    @classmethod
    def obtener_instancias_topico_disponibles(cls):
        """Obtiene todas las instancias de tópico disponibles para reportes"""
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
        resultados = execute_query(query)
        return [
            {
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
            for fila in resultados
        ]
    
    @classmethod
    def obtener_cursos_cerrados(cls):
        """Obtiene todas las instancias de curso cerradas para reportes"""
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
        resultados = execute_query(query)
        return [
            {
                'id': fila[0],
                'curso_codigo': fila[1],
                'curso_nombre': fila[2],
                'semestre': fila[3],
                'anio': fila[4],
                'fecha_cierre': fila[5],
                'total_secciones': fila[6],
                'display_name': f"{fila[1]} {fila[4]}{fila[3]:02d} - {fila[2]}"
            }
            for fila in resultados
        ]
    
    @classmethod
    def obtener_secciones_curso_cerrado(cls, instancia_curso_id):
        """Obtiene las secciones de un curso cerrado específico"""
        query = """
        SELECT DISTINCT
            s.numero,
            COUNT(DISTINCT nf.alumno_id) as total_alumnos
        FROM secciones s
        LEFT JOIN evaluaciones e ON e.seccion_id = s.id
        LEFT JOIN instancias_topico it ON it.evaluacion_id = e.id
        LEFT JOIN notas n ON n.instancia_topico_id = it.id
        LEFT JOIN notas_finales nf ON nf.alumno_id = n.alumno_id AND nf.instancia_curso_id = s.instancia_id
        WHERE s.instancia_id = ?
        GROUP BY s.numero
        ORDER BY s.numero
        """
        resultados = execute_query(query, (instancia_curso_id,))
        return [
            {
                'numero': fila[0],
                'total_alumnos': fila[1] or 0
            }
            for fila in resultados
        ]
    
    @classmethod
    def obtener_alumnos_con_cursos_cerrados(cls):
        """Obtiene alumnos que tienen cursos cerrados para certificado de notas"""
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
        resultados = execute_query(query)
        return [
            {
                'id': fila[0],
                'nombre': fila[1],
                'correo': fila[2],
                'total_cursos_cerrados': fila[3],                'display_name': f"{fila[1]} ({fila[2]}) - {fila[3]} curso(s) cerrado(s)"
            }
            for fila in resultados
        ]
    
    @classmethod
    def calcular_estadisticas_seccion(cls, notas):
        """Calcula estadísticas para una sección"""
        if not notas:
            return None
            
        notas_validas = [n for n in notas if n.get('nota_final') is not None]
        total_estudiantes = len(notas)
        
        if not notas_validas:
            return {
                'total_estudiantes': total_estudiantes,
                'promedio': None,
                'aprobados': 0,
                'reprobados': 0
            }
        
        promedio = sum(n['nota_final'] for n in notas_validas) / len(notas_validas)
        aprobados = len([n for n in notas_validas if n['nota_final'] >= 4.0])
        reprobados = len([n for n in notas_validas if n['nota_final'] < 4.0])
        
        return {
            'total_estudiantes': total_estudiantes,
            'promedio': promedio,
            'aprobados': aprobados,
            'reprobados': reprobados
        }
    
    @classmethod
    def calcular_estadisticas_seccion(cls, notas):
        """Calcula estadísticas para una sección"""
        if not notas:
            return None
            
        notas_validas = [n for n in notas if n.get('nota_final') is not None]
        total_estudiantes = len(notas)
        
        if not notas_validas:
            return {
                'total_estudiantes': total_estudiantes,
                'promedio': None,
                'aprobados': 0,
                'reprobados': 0
            }
        
        promedio = sum(n['nota_final'] for n in notas_validas) / len(notas_validas)
        aprobados = len([n for n in notas_validas if n['nota_final'] >= 4.0])
        reprobados = len([n for n in notas_validas if n['nota_final'] < 4.0])
        
        return {
            'total_estudiantes': total_estudiantes,
            'promedio': promedio,
            'aprobados': aprobados,
            'reprobados': reprobados
        }
    
    @classmethod
    def calcular_estadisticas_alumno(cls, certificado):
        """Calcula estadísticas para el certificado de un alumno"""
        if not certificado:
            return None
            
        notas_validas = [c for c in certificado if c.get('nota_final') is not None]
        total_cursos = len(certificado)
        
        if not notas_validas:
            return {
                'total_cursos': total_cursos,
                'promedio_general': None,
                'cursos_aprobados': 0,
                'cursos_reprobados': 0,
                'creditos_totales': 0
            }
        
        promedio_general = sum(c['nota_final'] for c in notas_validas) / len(notas_validas)
        cursos_aprobados = len([c for c in notas_validas if c['nota_final'] >= 4.0])
        cursos_reprobados = len([c for c in notas_validas if c['nota_final'] < 4.0])
        creditos_totales = sum(c.get('creditos', 0) or 0 for c in certificado)
        
        return {
            'total_cursos': total_cursos,
            'promedio_general': promedio_general,
            'cursos_aprobados': cursos_aprobados,
            'cursos_reprobados': cursos_reprobados,
            'creditos_totales': creditos_totales
        }
