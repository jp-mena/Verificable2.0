#!/usr/bin/env python3
"""
Script para probar los nuevos CRUDs de instancias y notas
"""

import sys
import os

# Agregar el directorio raíz al path para poder importar los modelos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import init_database
from models.curso import Curso
from models.instancia_curso import InstanciaCurso
from models.seccion import Seccion
from models.alumno import Alumno
from models.topico import Topico
from models.instancia_topico import InstanciaTopico
from models.evaluacion import Evaluacion
from models.nota import Nota

def test_instancias_curso():
    """Prueba la creación de instancias de curso"""
    print("=== Probando Instancias de Curso ===")
    
    # Obtener cursos existentes
    cursos = Curso.obtener_todos()
    if not cursos:
        print("❌ No hay cursos disponibles. Ejecuta create_sample_data.py primero.")
        return False
    
    curso_id = cursos[0][0]  # Tomar el primer curso
    print(f"📚 Usando curso ID: {curso_id}")
    
    try:
        # Crear instancia de curso
        instancia = InstanciaCurso.crear(1, 2025, curso_id)
        print(f"✅ Instancia de curso creada: ID {instancia.id}")
        
        # Listar todas las instancias
        instancias = InstanciaCurso.obtener_todos()
        print(f"📋 Total de instancias: {len(instancias)}")
        
        return True
    except Exception as e:
        print(f"❌ Error creando instancia de curso: {e}")
        return False

def test_secciones():
    """Prueba la creación de secciones"""
    print("\n=== Probando Secciones ===")
    
    # Obtener instancias existentes
    instancias = InstanciaCurso.obtener_todos()
    if not instancias:
        print("❌ No hay instancias de curso disponibles.")
        return False
    
    instancia_id = instancias[0]['id']
    print(f"🏫 Usando instancia ID: {instancia_id}")
    
    try:
        # Crear sección
        seccion = Seccion.crear(1, instancia_id)
        print(f"✅ Sección creada: ID {seccion.id}")
        
        # Listar todas las secciones
        secciones = Seccion.obtener_todos()
        print(f"📋 Total de secciones: {len(secciones)}")
        
        return True
    except Exception as e:
        print(f"❌ Error creando sección: {e}")
        return False

def test_topicos_y_evaluaciones():
    """Prueba la creación de tópicos y evaluaciones"""
    print("\n=== Probando Tópicos y Evaluaciones ===")
    
    try:
        # Crear tópico
        topico = Topico.crear("Variables y Tipos de Datos", "Introducción a variables")
        print(f"✅ Tópico creado: ID {topico.id}")
        
        # Crear evaluación
        evaluacion = Evaluacion.crear("Prueba 1", "PU", 30)
        print(f"✅ Evaluación creada: ID {evaluacion.id}")
        
        # Obtener instancias de curso
        instancias = InstanciaCurso.obtener_todos()
        if instancias:
            instancia_id = instancias[0]['id']
            
            # Crear instancia de tópico
            instancia_topico = InstanciaTopico.crear(topico.id, instancia_id, evaluacion.id)
            print(f"✅ Instancia de tópico creada: ID {instancia_topico.id}")
            
            return True
        else:
            print("❌ No hay instancias de curso disponibles.")
            return False
            
    except Exception as e:
        print(f"❌ Error creando tópicos/evaluaciones: {e}")
        return False

def test_notas():
    """Prueba la creación de notas"""
    print("\n=== Probando Notas ===")
    
    try:
        # Obtener alumnos existentes
        alumnos = Alumno.obtener_todos()
        if not alumnos:
            print("❌ No hay alumnos disponibles.")
            return False
        
        alumno_id = alumnos[0][0]
        print(f"👨‍🎓 Usando alumno ID: {alumno_id}")
        
        # Obtener instancias de tópico
        instancias_topico = InstanciaTopico.obtener_todos()
        if not instancias_topico:
            print("❌ No hay instancias de tópico disponibles.")
            return False
        
        instancia_topico_id = instancias_topico[0]['id']
        print(f"📝 Usando instancia de tópico ID: {instancia_topico_id}")
        
        # Crear nota
        nota = Nota.crear(alumno_id, instancia_topico_id, 6.5)
        print(f"✅ Nota creada: ID {nota.id} - Nota: 6.5")
        
        # Listar todas las notas
        notas = Nota.obtener_todos()
        print(f"📋 Total de notas: {len(notas)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando nota: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de los nuevos CRUDs...\n")
    
    # Inicializar base de datos
    init_database()
    
    # Ejecutar pruebas
    tests = [
        test_instancias_curso,
        test_secciones,
        test_topicos_y_evaluaciones,
        test_notas
    ]
    
    resultados = []
    for test in tests:
        resultado = test()
        resultados.append(resultado)
    
    # Resumen
    print("\n" + "="*50)
    print("🏁 RESUMEN DE PRUEBAS:")
    print(f"✅ Exitosas: {sum(resultados)}")
    print(f"❌ Fallidas: {len(resultados) - sum(resultados)}")
    
    if all(resultados):
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("Los CRUDs están funcionando correctamente.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()
