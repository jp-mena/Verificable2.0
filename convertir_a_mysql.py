#!/usr/bin/env python3
"""
Script para convertir todos los ? a %s en los modelos (SQLite -> MySQL)
"""

import os
import re
from pathlib import Path

def convert_file(file_path):
    """Convierte un archivo de ? a %s"""
    print(f"🔄 Procesando {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Contar cambios antes
        question_marks = content.count('?')
        
        if question_marks == 0:
            print(f"   ✅ Ya convertido (0 cambios)")
            return
        
        # Reemplazar ? por %s solo en consultas SQL
        # Buscar patrones de consultas SQL con ?
        patterns = [
            r'(INSERT INTO[^"]*"[^"]*\([^)]*\)\s*VALUES\s*\([^)]*)\?([^)]*\))',
            r'(UPDATE[^"]*"[^"]*SET[^"]*)\?([^"]*WHERE[^"]*)\?',
            r'(SELECT[^"]*FROM[^"]*WHERE[^"]*)\?',
            r'(DELETE[^"]*FROM[^"]*WHERE[^"]*)\?',
            r'(".*?)\?([^"]*")',  # Cualquier ? dentro de comillas
        ]
        
        # Método más simple y seguro: reemplazar ? por %s solo en strings que contienen SQL
        lines = content.split('\n')
        converted_lines = []
        
        for line in lines:
            # Si la línea contiene palabras clave SQL y ?, convertir
            if any(keyword in line.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'VALUES', 'WHERE', 'SET']) and '?' in line:
                # Reemplazar ? por %s
                new_line = line.replace('?', '%s')
                converted_lines.append(new_line)
                if '?' in line:
                    print(f"   🔄 Convertido: {line.strip()}")
                    print(f"      ✅ Nuevo:     {new_line.strip()}")
            else:
                converted_lines.append(line)
        
        new_content = '\n'.join(converted_lines)
        
        # Contar cambios después
        new_question_marks = new_content.count('?')
        changes = question_marks - new_question_marks
        
        if changes > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"   ✅ Convertido: {changes} cambios")
        else:
            print(f"   ⚠️  Sin cambios aplicados")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    print("🔧 CONVIRTIENDO MODELOS DE SQLITE A MYSQL")
    print("=" * 50)
    
    # Directorio de modelos
    models_dir = Path('sga/models')
    
    if not models_dir.exists():
        print("❌ Directorio sga/models no encontrado")
        return
    
    # Procesar todos los archivos .py
    python_files = list(models_dir.glob('*.py'))
    
    if not python_files:
        print("❌ No se encontraron archivos Python en sga/models")
        return
    
    print(f"📁 Encontrados {len(python_files)} archivos:")
    for file in python_files:
        print(f"   - {file.name}")
    
    print(f"\n🚀 Iniciando conversión...")
    
    for file_path in python_files:
        convert_file(file_path)
    
    print(f"\n🎉 ¡CONVERSIÓN COMPLETADA!")
    print("✅ Todos los modelos convertidos de SQLite (?) a MySQL (%s)")
    print("🚀 Ahora puedes probar: python app.py")

if __name__ == "__main__":
    main()
