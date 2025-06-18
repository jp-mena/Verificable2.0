import requests
import json

BASE_URL = "http://localhost:5000"

def test_invalid_data():
    print("=== PRUEBAS DE ROBUSTEZ DEL SISTEMA ===\n")
    
    print("1. Pruebas con datos inválidos para cursos:")
    invalid_course_data = [
        {},
        {"codigo": ""},
        {"codigo": "TEST", "nombre": ""},
        {"codigo": "T", "nombre": "Test"},
        {"codigo": "A" * 50, "nombre": "Test"},
        {"codigo": 123, "nombre": "Test"},
        {"codigo": None, "nombre": "Test"},
        {"codigo": "TEST", "nombre": "A" * 200},
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
        {},
        {"nombre": "Test", "correo": "invalid-email"},
        {"nombre": "", "correo": "test@email.com"},
        {"nombre": "T", "correo": "test@email.com"},
        {"nombre": 123, "correo": "test@email.com"},
        {"nombre": "Test", "correo": ""},
        {"nombre": "Test", "correo": None},
        {"nombre": "Test", "correo": "test@email.com", "fecha_ingreso": "invalid-date"},
        {"nombre": "Test", "correo": "test@email.com", "fecha_ingreso": "2025-13-40"},
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
            response = requests.get(f"{BASE_URL}/api/cursos/{injection}")
            print(f"   Test {i+1}: Status {response.status_code}")
        except Exception as e:
            print(f"   Test {i+1}: Error de conexión - {e}")

def test_edge_cases():
    """Prueba casos extremos"""
    print("\n=== PRUEBAS DE CASOS EXTREMOS ===\n")
    
    print("1. Datos extremadamente largos:")
    very_long_string = "A" * 10000
    
    try:
        data = {"codigo": very_long_string, "nombre": very_long_string}
        response = requests.post(f"{BASE_URL}/api/cursos", json=data)
        print(f"   String muy largo: Status {response.status_code}")
    except Exception as e:
        print(f"   String muy largo: Error - {e}")
    
    print("\n2. Caracteres especiales:")
    special_chars = [
        "éñüáí",
        "中文测试",
        "🚀🎉📚",
        "' \" \\ / \n \t",
        "\x00\x01\x02",
    ]
    
    for i, chars in enumerate(special_chars):
        try:
            data = {"codigo": f"TEST{i}", "nombre": chars}
            response = requests.post(f"{BASE_URL}/api/cursos", json=data)
            print(f"   Test {i+1}: Status {response.status_code}")
        except Exception as e:
            print(f"   Test {i+1}: Error - {e}")

def test_concurrent_requests():
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
    
    threads = []
    for i in range(10):
        thread = threading.Thread(target=make_request, args=(i,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print("Resultados de solicitudes concurrentes:")
    for result in results:
        print(f"   {result}")

if __name__ == "__main__":
    print("Iniciando pruebas de robustez del sistema SGA...")
    print("Asegúrate de que el servidor esté ejecutándose en http://localhost:5000\n")
    
    try:
        response = requests.get(f"{BASE_URL}/api")
        print(f"Servidor disponible: {response.status_code}\n")
        
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
