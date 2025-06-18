import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'sga_db'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'autocommit': True
}

def create_database_if_not_exists():
    """Crea la base de datos si no existe"""
    try:
        # Conectar sin especificar base de datos
        temp_config = DB_CONFIG.copy()
        temp_config.pop('database')
        
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Base de datos '{DB_CONFIG['database']}' lista")
        
        conn.close()
    except Error as e:
        print(f"❌ Error creando base de datos: {e}")

def init_database():
    """Inicializa la base de datos y crea las tablas necesarias"""
    try:
        # Primero crear la base de datos si no existe
        create_database_if_not_exists()
        
        # Conectar a la base de datos
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Tabla Cursos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cursos (
                id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
                codigo VARCHAR(10) UNIQUE NOT NULL,
                nombre VARCHAR(255) NOT NULL,
                creditos INT DEFAULT 4,
                requisitos TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Tabla Salas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salas (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(255) UNIQUE NOT NULL,
                capacidad INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')

        # Tabla Profesores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profesores (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(255) NOT NULL,
                correo VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Tabla Alumnos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alumnos (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(255) NOT NULL,
                correo VARCHAR(255) UNIQUE NOT NULL,
                fecha_ingreso DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Tabla Instancias de Curso
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS instancias_curso (
                id INT PRIMARY KEY AUTO_INCREMENT,
                semestre INT NOT NULL,
                anio INT NOT NULL,
                curso_id INT UNSIGNED NOT NULL,
                cerrado BOOLEAN DEFAULT 0,
                fecha_cierre TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (curso_id) REFERENCES cursos (id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Tabla Secciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS secciones (
                id INT PRIMARY KEY AUTO_INCREMENT,
                numero INT NOT NULL,
                instancia_id INT NOT NULL,
                profesor_id INT,
                sala_id INT,       
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (instancia_id) REFERENCES instancias_curso (id) ON DELETE CASCADE,
                FOREIGN KEY (profesor_id) REFERENCES profesores (id) ON DELETE SET NULL,
                FOREIGN KEY(sala_id) REFERENCES salas(id) ON DELETE SET NULL   
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Tabla Evaluaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluaciones (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(255) NOT NULL,
                porcentaje DECIMAL(5,2) NOT NULL,
                seccion_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seccion_id) REFERENCES secciones (id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Tabla Tópicos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topicos (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(255) NOT NULL,
                tipo VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Tabla Instancias de Tópico
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS instancias_topico (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(255) NOT NULL,
                peso DECIMAL(5,2) NOT NULL,
                opcional BOOLEAN DEFAULT 0,
                evaluacion_id INT NOT NULL,
                topico_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones (id) ON DELETE CASCADE,
                FOREIGN KEY (topico_id) REFERENCES topicos (id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Tabla Notas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas (
                id INT PRIMARY KEY AUTO_INCREMENT,
                alumno_id INT NOT NULL,
                instancia_topico_id INT NOT NULL,
                nota DECIMAL(3,1) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (alumno_id) REFERENCES alumnos (id) ON DELETE CASCADE,
                FOREIGN KEY (instancia_topico_id) REFERENCES instancias_topico (id) ON DELETE CASCADE,
                UNIQUE KEY unique_nota (alumno_id, instancia_topico_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Tabla Inscripciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inscripciones (
                id INT PRIMARY KEY AUTO_INCREMENT,
                alumno_id INT NOT NULL,
                instancia_curso_id INT NOT NULL,
                fecha_inscripcion DATE DEFAULT (CURDATE()),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (alumno_id) REFERENCES alumnos (id) ON DELETE CASCADE,
                FOREIGN KEY (instancia_curso_id) REFERENCES instancias_curso (id) ON DELETE CASCADE,
                UNIQUE KEY unique_inscripcion (alumno_id, instancia_curso_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')

        # Tabla Notas Finales (calculadas al cerrar curso)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas_finales (
                id INT PRIMARY KEY AUTO_INCREMENT,
                alumno_id INT NOT NULL,
                instancia_curso_id INT NOT NULL,
                nota_final DECIMAL(3,1) NOT NULL,
                fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (alumno_id) REFERENCES alumnos (id) ON DELETE CASCADE,
                FOREIGN KEY (instancia_curso_id) REFERENCES instancias_curso (id) ON DELETE CASCADE,
                UNIQUE KEY unique_nota_final (alumno_id, instancia_curso_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        

        # Tabla Bloques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bloques (
                id INT PRIMARY KEY AUTO_INCREMENT,
                dia INT NOT NULL,
                inicio TIME NOT NULL,
                fin TIME NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')

        # Tabla Horarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS horarios (
                id INT PRIMARY KEY AUTO_INCREMENT,
                seccion_id INT NOT NULL,
                bloque_id INT NOT NULL,
                sala_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seccion_id) REFERENCES secciones(id) ON DELETE CASCADE,
                FOREIGN KEY (bloque_id) REFERENCES bloques(id) ON DELETE CASCADE,
                FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE CASCADE,
                UNIQUE KEY unique_bloque_sala (bloque_id, sala_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')

        
        print("✅ Base de datos MySQL inicializada correctamente")
        
        cursor.execute("SELECT COUNT(*) FROM bloques")
        if cursor.fetchone()[0] == 0:
            horas = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]
            for d in range(1, 6):  # De lunes (1) a viernes (5)
                for h in horas:
                    fin = f"{int(h[:2])+1:02d}:{h[3:]}"
                    cursor.execute("INSERT INTO bloques (dia, inicio, fin) VALUES (%s, %s, %s)", (d, h, fin))
                    
        conn.commit()
        conn.close()
    except Error as e:
        print(f"❌ Error inicializando base de datos MySQL: {e}")

def get_connection():
    """Obtiene una conexión a la base de datos MySQL"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

def execute_query(query, params=None):
    """Ejecuta una consulta y retorna los resultados"""
    conn = get_connection()
    if not conn:
        return None
        
    try:
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
        
        return results
        
    except Error as e:
        print(f"❌ Error ejecutando consulta: {e}")
        print(f"Query: {query}")
        print(f"Params: {params}")
        conn.rollback()
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
