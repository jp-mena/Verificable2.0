# Sistema de Gestión Académica (SGA)

Un sistema web simple para gestionar cursos, profesores y alumnos universitarios. Desarrollado con Flask y SQLite.

## Estructura del Proyecto

```
proyecto4/
├── app.py              # Archivo principal de la aplicación
├── requirements.txt    # Dependencias del proyecto
├── plan.md            # Plan de desarrollo del proyecto
├── config/
│   └── settings.py    # Configuración de la aplicación
├── db/
│   └── database.py    # Configuración y conexión a la base de datos
├── models/
│   ├── curso.py       # Modelo y CRUD para Cursos
│   ├── profesor.py    # Modelo y CRUD para Profesores
│   └── alumno.py      # Modelo y CRUD para Alumnos
└── routes/
    ├── curso_routes.py    # Endpoints REST para Cursos
    ├── profesor_routes.py # Endpoints REST para Profesores
    └── alumno_routes.py   # Endpoints REST para Alumnos
```

## Instalación y Ejecución

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecutar la aplicación:
```bash
python app.py
```

3. La aplicación estará disponible en: http://127.0.0.1:5000

## Endpoints Disponibles

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
