#!/usr/bin/env python3
"""
Script para limpiar completamente la base de datos SGA
Elimina todos los datos de todas las tablas
"""

import os
import sys

# Agregar el directorio raíz al path para importar sga
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.insert(0, root_dir)

from sga.db.database import get_connection, DATABASE_PATH

def limpiar_base_datos():
    """Elimina todos los datos de todas las tablas"""
    
    # Verificar que existe la base de datos
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ No se encontró la base de datos en: {DATABASE_PATH}")
        return False
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Lista de todas las tablas en orden de dependencias (las que tienen FK al final)
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
        
        print("🧹 Iniciando limpieza de la base de datos...")
        
        # Desactivar restricciones de claves foráneas temporalmente
        cursor.execute('PRAGMA foreign_keys = OFF')
        
        # Eliminar datos de cada tabla
        for tabla in tablas:
            try:
                cursor.execute(f'DELETE FROM {tabla}')
                filas_eliminadas = cursor.rowcount
                print(f"✅ Tabla '{tabla}': {filas_eliminadas} registros eliminados")
            except Exception as e:
                print(f"⚠️  Error al limpiar tabla '{tabla}': {e}")
        
        # Resetear los autoincrement
        cursor.execute("DELETE FROM sqlite_sequence")
        print("✅ Contadores de ID reseteados")
        
        # Reactivar restricciones de claves foráneas
        cursor.execute('PRAGMA foreign_keys = ON')
        
        conn.commit()
        conn.close()
        
        print("\n🎉 ¡Base de datos limpiada exitosamente!")
        print("📊 Todas las tablas están ahora vacías")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        return False

def confirmar_limpieza():
    """Solicita confirmación antes de proceder"""
    print("⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos de la base de datos")
    print("📝 Se eliminarán:")
    print("   • Todos los profesores")
    print("   • Todos los alumnos") 
    print("   • Todos los cursos")
    print("   • Todas las instancias, secciones y evaluaciones")
    print("   • Todas las notas e inscripciones")
    print("   • Todos los tópicos")
    print()
    
    respuesta = input("¿Estás seguro de que quieres continuar? (escribe 'CONFIRMAR' para proceder): ")
    
    return respuesta.strip().upper() == 'CONFIRMAR'

if __name__ == "__main__":
    print("=" * 60)
    print("🗑️  LIMPIEZA COMPLETA DE BASE DE DATOS SGA")
    print("=" * 60)
    
    if confirmar_limpieza():
        if limpiar_base_datos():
            print("\n✨ ¡Limpieza completada! La base de datos está lista para usar.")
        else:
            print("\n❌ La limpieza falló. Revisa los errores anteriores.")
    else:
        print("\n🚫 Limpieza cancelada por el usuario.")
