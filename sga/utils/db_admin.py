"""
Utilidades para administración de la base de datos MySQL
"""

from sga.db.database import get_connection
import os

def limpiar_todas_las_tablas():
    """
    Limpia todos los datos de todas las tablas
    Retorna True si fue exitoso, False si hubo error
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Lista de tablas en orden de dependencias
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
        
        # Desactivar restricciones de claves foráneas
        cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
        
        # Eliminar datos de cada tabla
        for tabla in tablas:
            cursor.execute(f'DELETE FROM {tabla}')
            # Resetear auto_increment para cada tabla
            cursor.execute(f'ALTER TABLE {tabla} AUTO_INCREMENT = 1')
        
        # Reactivar restricciones
        cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error al limpiar base de datos: {e}")
        return False

def obtener_estadisticas_db():
    """
    Obtiene estadísticas de cuántos registros hay en cada tabla
    """
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
    """
    Verifica si la base de datos está completamente vacía
    """
    estadisticas = obtener_estadisticas_db()
    return all(count == 0 for count in estadisticas.values())
