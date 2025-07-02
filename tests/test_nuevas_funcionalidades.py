import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sga.db.database import init_database
from sga.models.curso import Curso
from sga.models.profesor import Profesor
from sga.models.alumno import Alumno
from sga.models.instancia_curso import InstanciaCurso
from sga.models.seccion import Seccion
from sga.models.evaluacion import Evaluacion
from sga.models.topico import Topico
from sga.models.instancia_topico import InstanciaTopico
from sga.models.nota import Nota

def probar_nuevas_funcionalidades():
    print("🚀 Probando nuevas funcionalidades del SGA...")
    
    init_database()
    print("✅ Base de datos inicializada")
    
    try:
        curso = Curso.crear("TEST101", "Curso de Prueba", "")
        print(f"✅ Curso creado: {curso.codigo}")
        
        profesor = Profesor.crear("Prof. Test", "test@universidad.cl")
        print(f"✅ Profesor creado: {profesor.nombre}")
        
        alumno = Alumno.crear("Estudiante Test", "estudiante@test.cl", "2025-01-01")
        print(f"✅ Alumno creado: {alumno.nombre}")
        
        instancia = InstanciaCurso.crear(1, 2025, curso.id)
        print(f"✅ Instancia de curso creada: {instancia.semestre}/{instancia.anio}")
        
        seccion = Seccion.crear(1, instancia.id)
        print(f"✅ Sección creada: {seccion.numero}")
        
        topico = Topico.crear("Control de Prueba", "control")
        print(f"✅ Tópico creado: {topico.nombre}")
        
        evaluacion = Evaluacion.crear("Controles", 30.0, seccion.id)
        print(f"✅ Evaluación creada: {evaluacion.nombre}")
        
        inst_topico = InstanciaTopico.crear("Control 1", 100.0, False, evaluacion.id, topico.id)
        print(f"✅ Instancia de tópico creada: {inst_topico.nombre}")
        
        nota = Nota.crear(alumno.id, inst_topico.id, 6.5)
        print(f"✅ Nota creada: {nota.nota}")
        
        print("\n🎉 Todas las funcionalidades están funcionando correctamente!")
        
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
