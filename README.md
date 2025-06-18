# Sistema de Gestión Académica (SGA)

Sistema web para gestionar cursos, profesores, alumnos, evaluaciones y notas universitarias. Desarrollado con Flask y SQLite.

## 🚀 Características

- **CRUD completo** para todas las entidades (cursos, profesores, alumnos, secciones, etc.)
- **Sistema de notas** con cálculo automático de notas finales por ponderación
- **Carga masiva** de datos desde archivos JSON
- **Interfaz web** intuitiva con Bootstrap

## 🛠️ Instalación y Ejecución

### 1. Preparar entorno
```bash
# Crear y activar entorno virtual
python -m venv venv


# macOS/Linux  
source venv/bin/activate

# windows 
.\venv\Scripts\Activate.ps1
```
### 2. Crear .env con credenciales

Debes tener un archivo .env en la raíz con al menos:
```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_clave
DB_NAME=sga_db
```
reemplazando `tu_clave` por tu clave real de mysql


### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar aplicación
```bash
python app.py
```

La aplicación estará disponible en: **http://127.0.0.1:5000**

## 🎯 Flujo de Uso de la Aplicación

### Para el evaluador: Dónde encontrar la funcionalidad

**1. Dashboard Principal (`/`)**
- Acceso a todas las funcionalidades principales
- Navegación por menús organizados

**2. Gestión CRUD - Menús principales:**
- **Cursos** (`/cursos`) - Crear, listar, editar, eliminar cursos
- **Profesores** (`/profesores`) - Gestión completa de profesores  
- **Alumnos** (`/alumnos`) - Registro y gestión de estudiantes
- **Instancias de Curso** (`/instancias-curso`) - Semestres/años con asignación de profesores
- **Secciones** (`/secciones`) - Organización de estudiantes e inscripciones
- **Evaluaciones** (`/evaluaciones`) - Tipos de evaluación con porcentajes
- **Tópicos** (`/topicos`) - Temas/unidades de curso
- **Instancias de Tópico** (`/instancias-topico`) - Configuración de pesos por tópico
- **Notas** (`/notas`) - Sistema de calificaciones con cálculo automático

**3. Funcionalidades especiales:**
- **Carga JSON** (`/cargar-json`) - Importación masiva de datos
- **API REST** (`/api/*`) - Endpoints para todas las entidades

### Flujo recomendado para pruebas:

1. **Cargar datos de ejemplo**: `/cargar-json` → "Cargar datos de ejemplo"
2. **Explorar entidades**: Usar los menús para ver CRUDs funcionando
3. **Crear notas**: Ir a "Notas" → "Crear" (formulario simple, sin wizard)
4. **Ver cálculos**: Las notas finales se calculan automáticamente con ponderación real

### Características del sistema de notas:
- **Cálculo automático** por peso de evaluaciones y tópicos
- **Validaciones** de integridad en todos los formularios  
- **Formulario simple** de creación (wizard eliminado)
- **Precisión** de 1 decimal en notas finales

## 📁 Estructura del Proyecto

```
Verificable2.0/
├── app.py                    # Archivo principal Flask
├── requirements.txt          # Dependencias
└── sga/                     # Paquete principal
    ├── config/              # Configuración
    ├── db/                  # Base de datos SQLite
    ├── models/              # Modelos de datos
    ├── routes/              # Rutas (Blueprint)
    ├── templates/           # Plantillas HTML
    ├── static/              # Archivos estáticos
    └── utils/               # Utilidades
```

## 🔧 Solución de Problemas


### Error "Module not found":
```bash
# Verificar entorno virtual activo (debe aparecer "(venv)")
pip install -r requirements.txt
```

