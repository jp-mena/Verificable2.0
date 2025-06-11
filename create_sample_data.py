"""
Script para agregar datos de ejemplo al sistema SGA
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import init_database
from models.curso import Curso
from models.profesor import Profesor
from models.alumno import Alumno

def create_sample_data():
    """Crea datos de ejemplo para el sistema"""
    print("Inicializando base de datos...")
    init_database()
    
    print("Creando cursos de ejemplo...")
    # Crear cursos
    curso1 = Curso("ICC5130", "Ingeniería de Software", "ICC2000, ICC3000")
    curso2 = Curso("ICC2000", "Programación Orientada a Objetos", "ICC1000")
    curso3 = Curso("ICC3000", "Estructuras de Datos", "ICC1000, ICC2000")
    curso4 = Curso("ICC1000", "Introducción a la Programación", "")
    
    curso1.save()
    curso2.save()
    curso3.save()
    curso4.save()
    
    print("Creando profesores de ejemplo...")
    # Crear profesores
    profesor1 = Profesor("Dr. Juan Pérez", "juan.perez@universidad.cl")
    profesor2 = Profesor("Dra. María González", "maria.gonzalez@universidad.cl")
    profesor3 = Profesor("Mg. Carlos López", "carlos.lopez@universidad.cl")
    profesor4 = Profesor("Dr. Ana Martínez", "ana.martinez@universidad.cl")
    
    profesor1.save()
    profesor2.save()
    profesor3.save()
    profesor4.save()
    
    print("Creando alumnos de ejemplo...")
    # Crear alumnos
    alumno1 = Alumno("Pedro Rodríguez", "pedro.rodriguez@estudiante.cl", "2024-03-01")
    alumno2 = Alumno("Sofía Chen", "sofia.chen@estudiante.cl", "2024-03-01")
    alumno3 = Alumno("Miguel Torres", "miguel.torres@estudiante.cl", "2023-08-01")
    alumno4 = Alumno("Valentina Silva", "valentina.silva@estudiante.cl", "2023-08-01")
    alumno5 = Alumno("Diego Morales", "diego.morales@estudiante.cl", "2024-01-15")
    
    alumno1.save()
    alumno2.save()
    alumno3.save()
    alumno4.save()
    alumno5.save()
    
    print("¡Datos de ejemplo creados exitosamente!")
    print("\nResumen:")
    print("- 4 cursos creados")
    print("- 4 profesores creados")
    print("- 5 alumnos creados")
    print("\nPuedes acceder a la aplicación en: http://127.0.0.1:5000")

if __name__ == "__main__":
    create_sample_data()
