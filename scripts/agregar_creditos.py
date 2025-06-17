#!/usr/bin/env python3
"""
Script para agregar el campo 'creditos' a la tabla cursos
"""

import os
import sys

# Agregar el directorio raíz al path para importar sga
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.insert(0, root_dir)

from sga.db.database import get_connection

def agregar_creditos_a_cursos():
    """Agrega el campo creditos a la tabla cursos"""
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar si el campo ya existe
        cursor.execute('PRAGMA table_info(cursos)')
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'creditos' in column_names:
            print("✅ El campo 'creditos' ya existe en la tabla cursos")
            return True
        
        print("🔧 Agregando campo 'creditos' a la tabla cursos...")
        
        # Agregar el campo creditos
        cursor.execute('ALTER TABLE cursos ADD COLUMN creditos INTEGER DEFAULT 4')
        
        conn.commit()
        conn.close()
        
        print("✅ Campo 'creditos' agregado exitosamente")
        print("📋 Valor por defecto: 4 créditos")
        return True
        
    except Exception as e:
        print(f"❌ Error al agregar campo creditos: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🔄 ACTUALIZACIÓN DE ESTRUCTURA DE BASE DE DATOS")
    print("=" * 50)
    
    if agregar_creditos_a_cursos():
        print("\n✨ ¡Actualización completada exitosamente!")
    else:
        print("\n❌ La actualización falló.")
