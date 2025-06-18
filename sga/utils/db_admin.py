from sga.db.database import get_connection
import os

def limpiar_todas_las_tablas():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        tablas = [
            'notas_finales',
            'notas', 
            'inscripciones',
            'instancias_topico',
            'evaluaciones',
            'secciones',
            'instancias_curso',
            'topicos',
            'alumnos',
            'profesores',
            'cursos'
        ]
        
        cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
        
        for tabla in tablas:
            cursor.execute(f'DELETE FROM {tabla}')
            cursor.execute(f'ALTER TABLE {tabla} AUTO_INCREMENT = 1')
        
        cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error al limpiar base de datos: {e}")
        return False

def obtener_estadisticas_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        tablas = [
            'cursos', 'profesores', 'alumnos', 'instancias_curso',
            'secciones', 'evaluaciones', 'topicos', 'instancias_topico',
            'notas', 'inscripciones', 'notas_finales'
        ]
        
        estadisticas = {}
        
        for tabla in tablas:
            cursor.execute(f'SELECT COUNT(*) FROM {tabla}')
            estadisticas[tabla] = cursor.fetchone()[0]
        
        conn.close()
        return estadisticas
        
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return {}

def verificar_db_vacia():
    estadisticas = obtener_estadisticas_db()
    return all(count == 0 for count in estadisticas.values())
