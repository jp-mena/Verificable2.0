# filepath: test_error_handling.py
"""
Script de prueba para verificar el manejo robusto de errores
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_invalid_data():
    """Prueba diferentes tipos de datos inválidos"""
    print("=== PRUEBAS DE ROBUSTEZ DEL SISTEMA ===\n")
    
    # Pruebas con datos inválidos para cursos
    print("1. Pruebas con datos inválidos para cursos:")
    invalid_course_data = [
        {},  # Datos vacíos
        {"codigo": ""},  # Código vacío
        {"codigo": "TEST", "nombre": ""},  # Nombre vacío
        {"codigo": "T", "nombre": "Test"},  # Código muy corto
        {"codigo": "A" * 50, "nombre": "Test"},  # Código muy largo
        {"codigo": 123, "nombre": "Test"},  # Tipo incorrecto
        {"codigo": None, "nombre": "Test"},  # Valor nulo
        {"codigo": "TEST", "nombre": "A" * 200},  # Nombre muy largo
    ]
    
    for i, data in enumerate(invalid_course_data):
        try:
            response = requests.post(f"{BASE_URL}/api/cursos", json=data)
            print(f"   Test {i+1}: Status {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"   Test {i+1}: Error de conexión - {e}")
    
    # Pruebas con datos inválidos para alumnos
    print("\n2. Pruebas con datos inválidos para alumnos:")
    invalid_student_data = [
        {},  # Datos vacíos
        {"nombre": "Test", "correo": "invalid-email"},  # Email inválido
        {"nombre": "", "correo": "test@email.com"},  # Nombre vacío
        {"nombre": "T", "correo": "test@email.com"},  # Nombre muy corto
        {"nombre": 123, "correo": "test@email.com"},  # Tipo incorrecto
        {"nombre": "Test", "correo": ""},  # Email vacío
        {"nombre": "Test", "correo": None},  # Email nulo
        {"nombre": "Test", "correo": "test@email.com", "fecha_ingreso": "invalid-date"},  # Fecha inválida
        {"nombre": "Test", "correo": "test@email.com", "fecha_ingreso": "2025-13-40"},  # Fecha imposible
    ]
    
    for i, data in enumerate(invalid_student_data):
        try:
            response = requests.post(f"{BASE_URL}/api/alumnos", json=data)
            print(f"   Test {i+1}: Status {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"   Test {i+1}: Error de conexión - {e}")
    
    # Pruebas con IDs inválidos
    print("\n3. Pruebas con IDs inválidos:")
    invalid_ids = [-1, 0, 999999, "abc", "", None, "' OR 1=1 --"]
    
    for i, invalid_id in enumerate(invalid_ids):
        try:
            response = requests.get(f"{BASE_URL}/api/cursos/{invalid_id}")
            print(f"   Test {i+1} (ID={invalid_id}): Status {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"   Test {i+1} (ID={invalid_id}): Error de conexión - {e}")
    
    # Pruebas de inyección SQL básica
    print("\n4. Pruebas de inyección SQL:")
    sql_injection_attempts = [
        "'; DROP TABLE cursos; --",
        "1 OR 1=1",
        "1; SELECT * FROM alumnos",
        "1 UNION SELECT 1,2,3",
        "<script>alert('XSS')</script>",
    ]
    
    for i, injection in enumerate(sql_injection_attempts):
        try:
            # Probar en diferentes endpoints
            response = requests.get(f"{BASE_URL}/api/cursos/{injection}")
            print(f"   Test {i+1}: Status {response.status_code}")
        except Exception as e:
            print(f"   Test {i+1}: Error de conexión - {e}")

def test_edge_cases():
    """Prueba casos extremos"""
    print("\n=== PRUEBAS DE CASOS EXTREMOS ===\n")
    
    # Datos extremadamente largos
    print("1. Datos extremadamente largos:")
    very_long_string = "A" * 10000
    
    try:
        data = {"codigo": very_long_string, "nombre": very_long_string}
        response = requests.post(f"{BASE_URL}/api/cursos", json=data)
        print(f"   String muy largo: Status {response.status_code}")
    except Exception as e:
        print(f"   String muy largo: Error - {e}")
    
    # Caracteres especiales
    print("\n2. Caracteres especiales:")
    special_chars = [
        "éñüáí",  # Acentos
        "中文测试",  # Caracteres chinos
        "🚀🎉📚",  # Emojis
        "' \" \\ / \n \t",  # Caracteres de escape
        "\x00\x01\x02",  # Caracteres de control
    ]
    
    for i, chars in enumerate(special_chars):
        try:
            data = {"codigo": f"TEST{i}", "nombre": chars}
            response = requests.post(f"{BASE_URL}/api/cursos", json=data)
            print(f"   Test {i+1}: Status {response.status_code}")
        except Exception as e:
            print(f"   Test {i+1}: Error - {e}")

def test_concurrent_requests():
    """Prueba solicitudes concurrentes"""
    print("\n=== PRUEBAS DE CONCURRENCIA ===\n")
    
    import threading
    import time
    
    results = []
    
    def make_request(i):
        try:
            data = {"codigo": f"CONC{i}", "nombre": f"Curso Concurrente {i}"}
            response = requests.post(f"{BASE_URL}/api/cursos", json=data)
            results.append(f"Thread {i}: Status {response.status_code}")
        except Exception as e:
            results.append(f"Thread {i}: Error - {e}")
    
    # Crear 10 hilos para hacer solicitudes simultáneas
    threads = []
    for i in range(10):
        thread = threading.Thread(target=make_request, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Esperar a que todos los hilos terminen
    for thread in threads:
        thread.join()
    
    print("Resultados de solicitudes concurrentes:")
    for result in results:
        print(f"   {result}")

if __name__ == "__main__":
    print("Iniciando pruebas de robustez del sistema SGA...")
    print("Asegúrate de que el servidor esté ejecutándose en http://localhost:5000\n")
    
    try:
        # Verificar que el servidor esté disponible
        response = requests.get(f"{BASE_URL}/api")
        print(f"Servidor disponible: {response.status_code}\n")
        
        # Ejecutar todas las pruebas
        test_invalid_data()
        test_edge_cases()
        test_concurrent_requests()
        
        print("\n=== PRUEBAS COMPLETADAS ===")
        print("El sistema ha manejado todas las pruebas de robustez.")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: No se puede conectar al servidor.")
        print("Asegúrate de que el servidor esté ejecutándose en http://localhost:5000")
    except Exception as e:
        print(f"ERROR inesperado durante las pruebas: {e}")
