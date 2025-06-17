#!/usr/bin/env python3
"""
Script para agregar el campo profesor_id a la tabla secciones
"""

import sys
import os
import sqlite3

# Agregar el directorio padre al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sga.db.database import DATABASE_PATH

def agregar_profesor_id_secciones():
    """Agrega el campo profesor_id a la tabla secciones"""
    try:
        print("Conectando a la base de datos...")
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(secciones)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'profesor_id' in columns:
            print("La columna profesor_id ya existe en la tabla secciones.")
            return
        
        print("Agregando columna profesor_id a la tabla secciones...")
        
        # Agregar la columna profesor_id
        cursor.execute('''
            ALTER TABLE secciones 
            ADD COLUMN profesor_id INTEGER 
            REFERENCES profesores(id) ON DELETE SET NULL
        ''')
        
        conn.commit()
        print("✅ Columna profesor_id agregada exitosamente.")
        
        # Verificar que se agregó correctamente
        cursor.execute("PRAGMA table_info(secciones)")
        columns = cursor.fetchall()
        print("\nEstructura actual de la tabla secciones:")
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
    except Exception as e:
        print(f"❌ Error al agregar la columna: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    agregar_profesor_id_secciones()
