# Sistema de Gestión Académica (SGA)

Un sistema web completo para gestionar cursos, profesores, alumnos, evaluaciones y notas universitarias. Desarrollado con Flask, SQLite y Bootstrap.

## 🚀 Características

- **Gestión de Cursos**: Crear, editar y eliminar cursos
- **Gestión de Profesores**: Administrar información de profesores
- **Gestión de Alumnos**: Registrar y mantener datos de estudiantes
- **Instancias de Curso**: Manejar semestres y años académicos
- **Secciones**: Organizar estudiantes por secciones
- **Evaluaciones**: Configurar diferentes tipos de evaluaciones
- **Tópicos**: Definir tipos de actividades académicas
- **Notas**: Registrar y consultar calificaciones
- **Carga Masiva**: Importar datos desde archivos JSON
- **Interfaz Web**: Dashboard intuitivo con Bootstrap

## Estructura del Proyecto

```
SGA/
├── app.py                    # Archivo principal de la aplicación
├── requirements.txt          # Dependencias del proyecto
├── plan.md                  # Plan de desarrollo del proyecto
├── config/
│   └── settings.py          # Configuración de la aplicación
├── db/
│   ├── database.py          # Configuración y conexión a la base de datos
│   └── sga.db              # Base de datos SQLite
├── models/                  # Modelos de datos
│   ├── curso.py
│   ├── profesor.py
│   ├── alumno.py
│   ├── instancia_curso.py
│   ├── seccion.py
│   ├── evaluacion.py
│   ├── topico.py
│   ├── instancia_topico.py
│   └── nota.py
├── routes/                  # Rutas de la aplicación
│   ├── curso_routes.py
│   ├── profesor_routes.py
│   ├── alumno_routes.py
│   ├── instancia_curso_routes.py
│   ├── seccion_routes.py
│   ├── evaluacion_routes.py
│   ├── topico_routes.py
│   ├── instancia_topico_routes.py
│   ├── nota_routes.py
│   └── json_routes.py
├── templates/               # Plantillas HTML
│   ├── base.html
│   ├── index.html
│   ├── instancias_curso/
│   ├── secciones/
│   ├── evaluaciones/
│   ├── topicos/
│   ├── instancias_topico/
│   ├── notas/
│   └── json/
├── static/
│   └── js/
│       └── app.js
└── data/
    └── json_examples/
        └── datos_ejemplo.json
```

## Instalación y Ejecución

1. **Clonar el repositorio o descargar los archivos**

2. **Instalar las dependencias:**
```bash
pip install -r requirements.txt
```

3. **Ejecutar la aplicación:**
```bash
python app.py
```

4. **Acceder a la aplicación:**
   - Interfaz Web: http://127.0.0.1:5000
   - API REST: http://127.0.0.1:5000/api

## 🌐 Funcionalidades Web

### Dashboard Principal
- Acceso rápido a todas las secciones
- Estadísticas básicas del sistema
- Navegación intuitiva

### Gestión de Entidades
- **Instancias de Curso**: Administrar semestres y años académicos
- **Secciones**: Organizar cursos por secciones
- **Evaluaciones**: Configurar evaluaciones con porcentajes
- **Tópicos**: Definir tipos de actividades (controles, tareas, proyectos, etc.)
- **Instancias de Tópico**: Configurar actividades específicas con pesos
- **Notas**: Registrar calificaciones de estudiantes

### Carga Masiva de Datos
- Importar datos desde archivos JSON
- Cargar datos de ejemplo predefinidos
- Validaciones automáticas de integridad

## 📊 API REST

### Cursos
- `GET /api/cursos` - Obtener todos los cursos
- `POST /api/cursos` - Crear un nuevo curso
- `GET /api/cursos/<id>` - Obtener un curso específico
- `PUT /api/cursos/<id>` - Actualizar un curso
- `DELETE /api/cursos/<id>` - Eliminar un curso

### Profesores
- `GET /api/profesores` - Obtener todos los profesores
- `POST /api/profesores` - Crear un nuevo profesor
- `GET /api/profesores/<id>` - Obtener un profesor específico
- `PUT /api/profesores/<id>` - Actualizar un profesor
- `DELETE /api/profesores/<id>` - Eliminar un profesor

### Alumnos
- `GET /api/alumnos` - Obtener todos los alumnos
- `POST /api/alumnos` - Crear un nuevo alumno
- `GET /api/alumnos/<id>` - Obtener un alumno específico
- `PUT /api/alumnos/<id>` - Actualizar un alumno
- `DELETE /api/alumnos/<id>` - Eliminar un alumno

## Ejemplos de Uso

### Crear un curso:
```json
POST /api/cursos
{
    "codigo": "ICC5130",
    "nombre": "Ingeniería de Software",
    "requisitos": "ICC2000, ICC3000"
}
```

### Crear un profesor:
```json
POST /api/profesores
{
    "nombre": "Juan Pérez",
    "correo": "juan.perez@universidad.cl"
}
```

### Crear un alumno:
```json
POST /api/alumnos
{
    "nombre": "María González",
    "correo": "maria.gonzalez@estudiante.cl",
    "fecha_ingreso": "2024-03-01"
}
```

## Funcionalidad de Carga Masiva JSON

### Interfaz Web
Accede a `/cargar-json` para usar la interfaz de carga masiva que incluye:

- **Carga por archivo**: Sube archivos JSON desde tu computadora
- **Drag & Drop**: Arrastra archivos directamente a la zona de carga
- **Datos de ejemplo**: Carga datos predefinidos para testing
- **Validación**: Valida la estructura JSON antes de cargar
- **Archivos de ejemplo**: Descarga plantillas JSON

### API REST para Carga JSON

#### Cargar datos
```bash
POST /api/cargar-json
Content-Type: application/json

{
  "cursos": [...],
  "profesores": [...],
  "alumnos": [...]
}
```

#### Validar estructura JSON
```bash
POST /api/validar-json
Content-Type: application/json

# Retorna información sobre la validez del JSON
```

### Formato JSON Soportado

El sistema acepta las siguientes entidades en el JSON:

```json
{
  "cursos": [
    {
      "codigo": "ICS1113",
      "nombre": "Programación", 
      "requisitos": ""
    }
  ],
  "profesores": [
    {
      "nombre": "Dr. Juan Pérez",
      "correo": "juan.perez@universidad.cl"
    }
  ],
  "alumnos": [
    {
      "nombre": "Ana Silva",
      "correo": "ana.silva@student.cl",
      "fecha_ingreso": "2024-03-01"
    }
  ],
  "instancias_curso": [
    {
      "semestre": 1,
      "anio": 2024,
      "curso_codigo": "ICS1113"
    }
  ],
  "secciones": [
    {
      "numero": 1,
      "instancia_curso": {
        "semestre": 1,
        "anio": 2024,
        "curso_codigo": "ICS1113"
      }
    }
  ],
  "topicos": [
    {
      "nombre": "Variables y Tipos de Datos",
      "descripcion": "Introducción a variables"
    }
  ],
  "evaluaciones": [
    {
      "nombre": "Controles",
      "tipo": "CO",
      "porcentaje": 40
    }
  ],
  "notas": [
    {
      "alumno_correo": "ana.silva@student.cl",
      "topico_nombre": "Variables y Tipos de Datos",
      "instancia_curso": {
        "semestre": 1,
        "anio": 2024,
        "curso_codigo": "ICS1113"
      },
      "nota": 6.5
    }
  ]
}
```

### Archivos de Ejemplo

- `static/examples/ejemplo_basico.json` - Datos básicos (cursos, profesores, alumnos)
- `static/examples/ejemplo_completo.json` - Todas las entidades con relaciones
