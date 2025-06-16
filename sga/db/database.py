import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'sga/db/sga.db'

def init_database():
    """Inicializa la base de datos y crea las tablas necesarias"""
    if not os.path.exists('sga/db'):
        os.makedirs('sga/db')
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Tabla Cursos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            requisitos TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla Profesores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profesores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
      # Tabla Alumnos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            fecha_ingreso DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
      # Tabla Instancias de Curso
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instancias_curso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semestre INTEGER NOT NULL,
            anio INTEGER NOT NULL,
            curso_id INTEGER NOT NULL,
            cerrado BOOLEAN DEFAULT 0,
            fecha_cierre TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (curso_id) REFERENCES cursos (id) ON DELETE CASCADE
        )
    ''')
    
    # Tabla Secciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS secciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER NOT NULL,
            instancia_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (instancia_id) REFERENCES instancias_curso (id) ON DELETE CASCADE
        )
    ''')
    
    # Tabla Evaluaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            porcentaje REAL NOT NULL,
            seccion_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seccion_id) REFERENCES secciones (id) ON DELETE CASCADE
        )
    ''')
    
    # Tabla Tópicos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla Instancias de Tópico
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instancias_topico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            peso REAL NOT NULL,
            opcional BOOLEAN DEFAULT 0,
            evaluacion_id INTEGER NOT NULL,
            topico_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones (id) ON DELETE CASCADE,
            FOREIGN KEY (topico_id) REFERENCES topicos (id) ON DELETE CASCADE
        )
    ''')
    
    # Tabla Notas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER NOT NULL,
            instancia_topico_id INTEGER NOT NULL,
            nota REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id) ON DELETE CASCADE,
            FOREIGN KEY (instancia_topico_id) REFERENCES instancias_topico (id) ON DELETE CASCADE,
            UNIQUE(alumno_id, instancia_topico_id)
        )
    ''')
      # Tabla Inscripciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inscripciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER NOT NULL,
            instancia_curso_id INTEGER NOT NULL,
            fecha_inscripcion DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id) ON DELETE CASCADE,
            FOREIGN KEY (instancia_curso_id) REFERENCES instancias_curso (id) ON DELETE CASCADE,
            UNIQUE(alumno_id, instancia_curso_id)
        )
    ''')

    # Tabla Notas Finales (calculadas al cerrar curso)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas_finales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER NOT NULL,
            instancia_curso_id INTEGER NOT NULL,
            nota_final REAL NOT NULL,
            fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id) ON DELETE CASCADE,
            FOREIGN KEY (instancia_curso_id) REFERENCES instancias_curso (id) ON DELETE CASCADE,
            UNIQUE(alumno_id, instancia_curso_id)
        )
    ''')
    
    # Agregar campos a tablas existentes si no existen
    try:
        cursor.execute('ALTER TABLE instancias_curso ADD COLUMN cerrado BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # El campo ya existe
    
    try:
        cursor.execute('ALTER TABLE instancias_curso ADD COLUMN fecha_cierre TIMESTAMP NULL')
    except sqlite3.OperationalError:
        pass  # El campo ya existe

    conn.commit()
    conn.close()

def get_connection():
    """Obtiene una conexión a la base de datos"""
    return sqlite3.connect(DATABASE_PATH)

def execute_query(query, params=None):
    """Ejecuta una consulta y retorna los resultados"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    if query.strip().upper().startswith('SELECT'):
        results = cursor.fetchall()
    else:
        conn.commit()
        results = cursor.lastrowid
    
    conn.close()
    return results
