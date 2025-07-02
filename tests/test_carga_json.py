import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sga.db.database import init_database
from sga.routes.json_routes import procesar_datos_json

def test_carga_basica():
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
    print("\n=== Probando Carga JSON Completa ===")
    
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
    print("\n=== Probando Validación de Errores ===")
    
    datos_con_errores = {
        "cursos": [
            {"codigo": "", "nombre": "Curso Sin Código", "requisitos": ""},
            {"codigo": "VALID01", "nombre": "", "requisitos": ""}
        ],
        "alumnos": [
            {"nombre": "Alumno Sin Correo", "fecha_ingreso": "2024-03-01"}
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
    print("\n=== Limpiando Datos de Prueba ===")
    
    try:
        from sga.db.database import execute_query
        
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
    print("🧪 Iniciando pruebas de carga JSON...\n")
    
    init_database()
    
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
    
    limpiar_datos_prueba()
    
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
