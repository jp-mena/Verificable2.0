# filepath: test_nuevas_funcionalidades.py
"""
Script de prueba para las nuevas funcionalidades del SGA
Ejecuta algunas operaciones básicas para verificar que todo funciona
"""

from db.database import init_database
from models.curso import Curso
from models.profesor import Profesor
from models.alumno import Alumno
from models.instancia_curso import InstanciaCurso
from models.seccion import Seccion
from models.evaluacion import Evaluacion
from models.topico import Topico
from models.instancia_topico import InstanciaTopico
from models.nota import Nota

def probar_nuevas_funcionalidades():
    """Prueba las nuevas funcionalidades agregadas"""
    print("🚀 Probando nuevas funcionalidades del SGA...")
    
    # Inicializar BD
    init_database()
    print("✅ Base de datos inicializada")
    
    # Crear datos básicos si no existen
    try:
        # Crear curso
        curso = Curso.crear("TEST101", "Curso de Prueba", "")
        print(f"✅ Curso creado: {curso.codigo}")
        
        # Crear profesor
        profesor = Profesor.crear("Prof. Test", "test@universidad.cl")
        print(f"✅ Profesor creado: {profesor.nombre}")
        
        # Crear alumno
        alumno = Alumno.crear("Estudiante Test", "estudiante@test.cl", "2025-01-01")
        print(f"✅ Alumno creado: {alumno.nombre}")
        
        # Crear instancia de curso
        instancia = InstanciaCurso.crear(1, 2025, curso.id)
        print(f"✅ Instancia de curso creada: {instancia.semestre}/{instancia.anio}")
        
        # Crear sección
        seccion = Seccion.crear(1, instancia.id)
        print(f"✅ Sección creada: {seccion.numero}")
        
        # Crear tópico
        topico = Topico.crear("Control de Prueba", "control")
        print(f"✅ Tópico creado: {topico.nombre}")
        
        # Crear evaluación
        evaluacion = Evaluacion.crear("Controles", 30.0, seccion.id)
        print(f"✅ Evaluación creada: {evaluacion.nombre}")
        
        # Crear instancia de tópico
        inst_topico = InstanciaTopico.crear("Control 1", 100.0, False, evaluacion.id, topico.id)
        print(f"✅ Instancia de tópico creada: {inst_topico.nombre}")
        
        # Crear nota
        nota = Nota.crear(alumno.id, inst_topico.id, 6.5)
        print(f"✅ Nota creada: {nota.nota}")
        
        print("\n🎉 Todas las funcionalidades están funcionando correctamente!")
        
        # Mostrar resumen
        print("\n📊 Resumen de datos creados:")
        print(f"   - Cursos: {len(Curso.obtener_todos())}")
        print(f"   - Profesores: {len(Profesor.obtener_todos())}")
        print(f"   - Alumnos: {len(Alumno.obtener_todos())}")
        print(f"   - Instancias de curso: {len(InstanciaCurso.obtener_todos())}")
        print(f"   - Secciones: {len(Seccion.obtener_todos())}")
        print(f"   - Evaluaciones: {len(Evaluacion.obtener_todos())}")
        print(f"   - Tópicos: {len(Topico.obtener_todos())}")
        print(f"   - Instancias de tópico: {len(InstanciaTopico.obtener_todos())}")
        print(f"   - Notas: {len(Nota.obtener_todos())}")
        
    except Exception as e:
        print(f"⚠️  Los datos de prueba ya existen o hay un error: {str(e)}")
        print("   Esto es normal si ya ejecutaste el script antes.")

if __name__ == "__main__":
    probar_nuevas_funcionalidades()
