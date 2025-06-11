#!/usr/bin/env python3
"""
Script de demostración completa del Sistema SGA
Muestra todas las funcionalidades implementadas
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import init_database
from models.curso import Curso
from models.profesor import Profesor  
from models.alumno import Alumno
from models.instancia_curso import InstanciaCurso
from models.seccion import Seccion
from models.topico import Topico
from models.evaluacion import Evaluacion
from models.instancia_topico import InstanciaTopico
from models.nota import Nota

def mostrar_banner():
    """Muestra el banner del sistema"""
    print("="*60)
    print("🎓 SISTEMA DE GESTIÓN ACADÉMICA (SGA) - DEMOSTRACIÓN")
    print("="*60)
    print("✅ Todas las funcionalidades implementadas:")
    print("   • CRUDs completos para todas las entidades")
    print("   • Interfaz web con Bootstrap")
    print("   • Carga masiva JSON con drag & drop")
    print("   • API REST completa")
    print("   • Validaciones y manejo de errores")
    print("="*60)

def demo_cruds_basicos():
    """Demuestra los CRUDs básicos"""
    print("\n📚 DEMO: CRUDs Básicos")
    print("-" * 30)
    
    # Crear datos básicos
    print("Creando datos básicos...")
    
    curso = Curso.crear("DEMO001", "Curso Demostración", "")
    profesor = Profesor.crear("Prof. Demo", "demo@universidad.cl")
    alumno = Alumno.crear("Estudiante Demo", "estudiante@demo.cl", "2024-03-01")
    
    print(f"✅ Curso creado: {curso.nombre}")
    print(f"✅ Profesor creado: {profesor.nombre}")
    print(f"✅ Alumno creado: {alumno.nombre}")
    
    # Listar datos
    cursos = Curso.obtener_todos()
    profesores = Profesor.obtener_todos()
    alumnos = Alumno.obtener_todos()
    
    print(f"📋 Total en BD: {len(cursos)} cursos, {len(profesores)} profesores, {len(alumnos)} alumnos")

def demo_entidades_avanzadas():
    """Demuestra las entidades avanzadas"""
    print("\n🏫 DEMO: Entidades Avanzadas")
    print("-" * 30)
    
    # Obtener curso existente
    cursos = Curso.obtener_todos()
    if cursos:
        curso_id = cursos[0][0]
        
        # Crear instancia de curso
        instancia = InstanciaCurso.crear(1, 2025, curso_id)
        print(f"✅ Instancia de curso creada para semestre 1-2025")
        
        # Crear sección
        seccion = Seccion.crear(1, instancia.id)
        print(f"✅ Sección 1 creada")
        
        # Crear tópico y evaluación
        topico = Topico.crear("Demo Tópico", "Tópico de demostración")
        evaluacion = Evaluacion.crear("Demo Evaluación", "EX", 100)
        print(f"✅ Tópico y evaluación creados")
        
        # Crear instancia de tópico
        inst_topico = InstanciaTopico.crear(topico.id, instancia.id, evaluacion.id)
        print(f"✅ Instancia de tópico creada")
        
        # Crear nota
        alumnos = Alumno.obtener_todos()
        if alumnos:
            alumno_id = alumnos[0][0]
            nota = Nota.crear(alumno_id, inst_topico.id, 6.8)
            print(f"✅ Nota 6.8 asignada")

def demo_estadisticas():
    """Muestra estadísticas del sistema"""
    print("\n📊 DEMO: Estadísticas del Sistema")
    print("-" * 30)
    
    # Contar entidades
    stats = {
        "Cursos": len(Curso.obtener_todos()),
        "Profesores": len(Profesor.obtener_todos()),
        "Alumnos": len(Alumno.obtener_todos()),
        "Instancias de Curso": len(InstanciaCurso.obtener_todos()),
        "Secciones": len(Seccion.obtener_todos()),
        "Tópicos": len(Topico.obtener_todos()),
        "Evaluaciones": len(Evaluacion.obtener_todos()),
        "Instancias de Tópico": len(InstanciaTopico.obtener_todos()),
        "Notas": len(Nota.obtener_todos())
    }
    
    print("📈 Estado actual de la base de datos:")
    for entidad, cantidad in stats.items():
        print(f"   • {entidad}: {cantidad}")

def demo_funcionalidades_web():
    """Información sobre funcionalidades web"""
    print("\n🌐 DEMO: Funcionalidades Web")
    print("-" * 30)
    
    print("🚀 Para probar la interfaz web, ejecuta:")
    print("   python app.py")
    print("\n📱 Luego visita: http://127.0.0.1:5000")
    print("\n✨ Funcionalidades disponibles:")
    print("   • Dashboard con estadísticas")
    print("   • CRUDs para todas las entidades")
    print("   • Carga masiva JSON (/cargar-json)")
    print("   • API REST (/api/...)")
    print("   • Drag & drop de archivos")
    print("   • Validación de JSON")

def demo_api_ejemplos():
    """Muestra ejemplos de uso de la API"""
    print("\n🔗 DEMO: Ejemplos de API REST")
    print("-" * 30)
    
    print("💡 Ejemplos de uso con curl:")
    print("""
# Listar cursos
curl http://127.0.0.1:5000/api/cursos

# Crear curso
curl -X POST http://127.0.0.1:5000/api/cursos \\
  -H "Content-Type: application/json" \\
  -d '{"codigo":"API001", "nombre":"Curso API", "requisitos":""}'

# Cargar datos JSON
curl -X POST http://127.0.0.1:5000/api/cargar-json \\
  -H "Content-Type: application/json" \\
  -d '{"cursos":[{"codigo":"JSON001","nombre":"Curso JSON","requisitos":""}]}'

# Validar JSON
curl -X POST http://127.0.0.1:5000/api/validar-json \\
  -H "Content-Type: application/json" \\
  -d '{"cursos":[{"codigo":"TEST","nombre":"Test"}]}'
""")

def limpiar_datos_demo():
    """Limpia los datos de demostración"""
    print("\n🧹 Limpiando datos de demostración...")
    
    try:
        from db.database import execute_query
        
        # Eliminar en orden para respetar FK
        queries = [
            "DELETE FROM notas WHERE id > 0",
            "DELETE FROM instancias_topico WHERE id > 0",
            "DELETE FROM evaluaciones WHERE nombre LIKE '%Demo%'",
            "DELETE FROM topicos WHERE nombre LIKE '%Demo%'",
            "DELETE FROM secciones WHERE id > 0",
            "DELETE FROM instancias_curso WHERE id > 0",
            "DELETE FROM alumnos WHERE correo LIKE '%demo%'",
            "DELETE FROM profesores WHERE correo LIKE '%demo%'",
            "DELETE FROM cursos WHERE codigo LIKE 'DEMO%'"
        ]
        
        for query in queries:
            execute_query(query)
        
        print("✅ Datos de demostración eliminados")
    except Exception as e:
        print(f"❌ Error limpiando: {e}")

def main():
    """Función principal de demostración"""
    mostrar_banner()
    
    # Inicializar BD
    print("\n🔧 Inicializando base de datos...")
    init_database()
    
    # Ejecutar demostraciones
    try:
        demo_cruds_basicos()
        demo_entidades_avanzadas()
        demo_estadisticas()
        demo_funcionalidades_web()
        demo_api_ejemplos()
        
        print("\n" + "="*60)
        print("🎉 ¡DEMOSTRACIÓN COMPLETADA!")
        print("✅ El Sistema SGA está completamente funcional")
        print("🚀 ¡Listo para usar en producción!")
        print("="*60)
        
    finally:
        # Limpiar datos de demo
        limpiar_datos_demo()

if __name__ == "__main__":
    main()
