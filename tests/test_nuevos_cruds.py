import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sga.db.database import init_database
from sga.models.curso import Curso
from sga.models.instancia_curso import InstanciaCurso
from sga.models.seccion import Seccion
from sga.models.alumno import Alumno
from sga.models.topico import Topico
from sga.models.instancia_topico import InstanciaTopico
from sga.models.evaluacion import Evaluacion
from sga.models.nota import Nota

def test_instancias_curso():
    print("=== Probando Instancias de Curso ===")
    
    cursos = Curso.obtener_todos()
    if not cursos:
        print("❌ No hay cursos disponibles. Ejecuta create_sample_data.py primero.")
        return False
    
    curso_id = cursos[0][0]
    print(f"📚 Usando curso ID: {curso_id}")
    
    try:
        instancia = InstanciaCurso.crear(1, 2025, curso_id)
        print(f"✅ Instancia de curso creada: ID {instancia.id}")
        
        instancias = InstanciaCurso.obtener_todos()
        print(f"📋 Total de instancias: {len(instancias)}")
        
        return True
    except Exception as e:
        print(f"❌ Error creando instancia de curso: {e}")
        return False

def test_secciones():
    print("\n=== Probando Secciones ===")
    
    instancias = InstanciaCurso.obtener_todos()
    if not instancias:
        print("❌ No hay instancias de curso disponibles.")
        return False
    
    instancia_id = instancias[0]['id']
    print(f"🏫 Usando instancia ID: {instancia_id}")
    
    try:
        seccion = Seccion.crear(1, instancia_id)
        print(f"✅ Sección creada: ID {seccion.id}")
        
        secciones = Seccion.obtener_todos()
        print(f"📋 Total de secciones: {len(secciones)}")
        
        return True
    except Exception as e:
        print(f"❌ Error creando sección: {e}")
        return False

def test_topicos_y_evaluaciones():
    print("\n=== Probando Tópicos y Evaluaciones ===")
    
    try:
        topico = Topico.crear("Variables y Tipos de Datos", "Introducción a variables")
        print(f"✅ Tópico creado: ID {topico.id}")
        
        evaluacion = Evaluacion.crear("Prueba 1", "PU", 30)
        print(f"✅ Evaluación creada: ID {evaluacion.id}")
        
        instancias = InstanciaCurso.obtener_todos()
        if instancias:
            instancia_id = instancias[0]['id']
            
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
    print("\n=== Probando Notas ===")
    
    try:
        alumnos = Alumno.obtener_todos()
        if not alumnos:
            print("❌ No hay alumnos disponibles.")
            return False
        
        alumno_id = alumnos[0][0]
        print(f"👨‍🎓 Usando alumno ID: {alumno_id}")
        
        instancias_topico = InstanciaTopico.obtener_todos()
        if not instancias_topico:
            print("❌ No hay instancias de tópico disponibles.")
            return False
        
        instancia_topico_id = instancias_topico[0]['id']
        print(f"📝 Usando instancia de tópico ID: {instancia_topico_id}")
        
        nota = Nota.crear(alumno_id, instancia_topico_id, 6.5)
        print(f"✅ Nota creada: ID {nota.id} - Nota: 6.5")
        
        notas = Nota.obtener_todos()
        print(f"📋 Total de notas: {len(notas)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando nota: {e}")
        return False

def main():
    print("🚀 Iniciando pruebas de los nuevos CRUDs...\n")
    
    init_database()
    
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
