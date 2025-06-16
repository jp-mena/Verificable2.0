#!/usr/bin/env python3
"""
Script para probar la funcionalidad de carga JSON masiva
"""

import sys
import os
import json

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sga.db.database import init_database
from sga.routes.json_routes import procesar_datos_json

def test_carga_basica():
    """Prueba la carga básica de datos JSON"""
    print("=== Probando Carga JSON Básica ===")
    
    datos_prueba = {
        "cursos": [
            {"codigo": "TEST001", "nombre": "Curso de Prueba", "requisitos": ""},
            {"codigo": "TEST002", "nombre": "Curso Avanzado", "requisitos": "TEST001"}
        ],
        "profesores": [
            {"nombre": "Prof. Prueba", "correo": "prof.prueba@test.cl"}
        ],
        "alumnos": [
            {"nombre": "Estudiante Test", "correo": "estudiante@test.cl", "fecha_ingreso": "2024-03-01"}
        ]
    }
    
    try:
        resultado = procesar_datos_json(datos_prueba)
        print(f"✅ Resultado: {resultado}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_carga_completa():
    """Prueba la carga completa con todas las entidades"""
    print("\n=== Probando Carga JSON Completa ===")
    
    # Leer el archivo de ejemplo completo
    try:
        with open('static/examples/ejemplo_completo.json', 'r', encoding='utf-8') as f:
            datos_completos = json.load(f)
        
        resultado = procesar_datos_json(datos_completos)
        print(f"✅ Resultado: {resultado}")
        return True
    except FileNotFoundError:
        print("❌ Archivo ejemplo_completo.json no encontrado")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_validacion_errores():
    """Prueba el manejo de errores en la carga JSON"""
    print("\n=== Probando Validación de Errores ===")
    
    # Datos con errores intencionados
    datos_con_errores = {
        "cursos": [
            {"codigo": "", "nombre": "Curso Sin Código", "requisitos": ""},  # Error: código vacío
            {"codigo": "VALID01", "nombre": "", "requisitos": ""}  # Error: nombre vacío
        ],
        "alumnos": [
            {"nombre": "Alumno Sin Correo", "fecha_ingreso": "2024-03-01"}  # Error: falta correo
        ]
    }
    
    try:
        resultado = procesar_datos_json(datos_con_errores)
        print(f"📋 Resultado (con errores esperados): {resultado}")
        return True
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_archivo_ejemplo():
    """Verifica que los archivos de ejemplo sean válidos"""
    print("\n=== Verificando Archivos de Ejemplo ===")
    
    archivos = [
        'static/examples/ejemplo_basico.json',
        'static/examples/ejemplo_completo.json'
    ]
    
    for archivo in archivos:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            print(f"✅ {archivo}: JSON válido")
        except FileNotFoundError:
            print(f"❌ {archivo}: Archivo no encontrado")
        except json.JSONDecodeError as e:
            print(f"❌ {archivo}: JSON inválido - {e}")
        except Exception as e:
            print(f"❌ {archivo}: Error - {e}")

def limpiar_datos_prueba():
    """Limpia los datos de prueba de la base de datos"""
    print("\n=== Limpiando Datos de Prueba ===")
    
    try:
        from db.database import execute_query
        
        # Eliminar datos de prueba
        queries = [
            "DELETE FROM notas WHERE id > 0",
            "DELETE FROM instancias_topico WHERE id > 0", 
            "DELETE FROM evaluaciones WHERE id > 0",
            "DELETE FROM topicos WHERE id > 0",
            "DELETE FROM secciones WHERE id > 0",
            "DELETE FROM instancias_curso WHERE id > 0",
            "DELETE FROM alumnos WHERE correo LIKE '%test%' OR correo LIKE '%prueba%'",
            "DELETE FROM profesores WHERE correo LIKE '%test%' OR correo LIKE '%prueba%'",
            "DELETE FROM cursos WHERE codigo LIKE 'TEST%'"
        ]
        
        for query in queries:
            execute_query(query)
        
        print("✅ Datos de prueba eliminados")
    except Exception as e:
        print(f"❌ Error limpiando datos: {e}")

def main():
    """Función principal"""
    print("🧪 Iniciando pruebas de carga JSON...\n")
    
    # Inicializar base de datos
    init_database()
    
    # Ejecutar pruebas
    tests = [
        test_archivo_ejemplo,
        test_carga_basica,
        test_validacion_errores,
        test_carga_completa
    ]
    
    resultados = []
    for test in tests:
        resultado = test()
        resultados.append(resultado)
    
    # Limpiar después de las pruebas
    limpiar_datos_prueba()
    
    # Resumen
    print("\n" + "="*50)
    print("🏁 RESUMEN DE PRUEBAS JSON:")
    print(f"✅ Exitosas: {sum(r for r in resultados if r)}")
    print(f"❌ Fallidas: {sum(r for r in resultados if not r)}")
    
    if all(resultados):
        print("\n🎉 ¡Todas las pruebas de carga JSON pasaron!")
        print("La funcionalidad de carga masiva está lista.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()
