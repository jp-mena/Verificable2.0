# Pruebas Manuales del Sistema SGA

## Instrucciones para probar la API

### 1. Verificar que la aplicación está funcionando
Abre tu navegador y ve a: http://127.0.0.1:5000

Deberías ver un mensaje de bienvenida con información sobre los endpoints disponibles.

### 2. Probar con curl (desde terminal)

#### Obtener todos los cursos:
```bash
curl -X GET http://127.0.0.1:5000/api/cursos
```

#### Crear un curso:
```bash
curl -X POST http://127.0.0.1:5000/api/cursos -H "Content-Type: application/json" -d "{\"codigo\": \"ICC5130\", \"nombre\": \"Ingeniería de Software\", \"requisitos\": \"ICC2000, ICC3000\"}"
```

#### Crear un profesor:
```bash
curl -X POST http://127.0.0.1:5000/api/profesores -H "Content-Type: application/json" -d "{\"nombre\": \"Juan Pérez\", \"correo\": \"juan.perez@universidad.cl\"}"
```

#### Crear un alumno:
```bash
curl -X POST http://127.0.0.1:5000/api/alumnos -H "Content-Type: application/json" -d "{\"nombre\": \"María González\", \"correo\": \"maria.gonzalez@estudiante.cl\", \"fecha_ingreso\": \"2024-03-01\"}"
```

#### Obtener todos los profesores:
```bash
curl -X GET http://127.0.0.1:5000/api/profesores
```

#### Obtener todos los alumnos:
```bash
curl -X GET http://127.0.0.1:5000/api/alumnos
```

#### Obtener un curso específico (ID 1):
```bash
curl -X GET http://127.0.0.1:5000/api/cursos/1
```

#### Actualizar un curso (ID 1):
```bash
curl -X PUT http://127.0.0.1:5000/api/cursos/1 -H "Content-Type: application/json" -d "{\"codigo\": \"ICC5130\", \"nombre\": \"Ingeniería de Software Avanzada\", \"requisitos\": \"ICC2000, ICC3000, ICC4000\"}"
```

#### Eliminar un curso (ID 1):
```bash
curl -X DELETE http://127.0.0.1:5000/api/cursos/1
```

### 3. Probar con herramientas como Postman o Thunder Client

Si prefieres una interfaz gráfica, puedes usar:
- **Postman**: https://www.postman.com/
- **Thunder Client** (extensión de VS Code)
- **Insomnia**: https://insomnia.rest/

### 4. Endpoints disponibles:

**Base URL**: http://127.0.0.1:5000

#### Cursos:
- GET /api/cursos - Listar todos los cursos
- POST /api/cursos - Crear curso
- GET /api/cursos/{id} - Obtener curso específico
- PUT /api/cursos/{id} - Actualizar curso
- DELETE /api/cursos/{id} - Eliminar curso

#### Profesores:
- GET /api/profesores - Listar todos los profesores
- POST /api/profesores - Crear profesor
- GET /api/profesores/{id} - Obtener profesor específico
- PUT /api/profesores/{id} - Actualizar profesor
- DELETE /api/profesores/{id} - Eliminar profesor

#### Alumnos:
- GET /api/alumnos - Listar todos los alumnos
- POST /api/alumnos - Crear alumno
- GET /api/alumnos/{id} - Obtener alumno específico
- PUT /api/alumnos/{id} - Actualizar alumno
- DELETE /api/alumnos/{id} - Eliminar alumno

### 5. Formato de datos

#### Curso:
```json
{
    "codigo": "ICC5130",
    "nombre": "Ingeniería de Software",
    "requisitos": "ICC2000, ICC3000" // Opcional
}
```

#### Profesor:
```json
{
    "nombre": "Juan Pérez",
    "correo": "juan.perez@universidad.cl"
}
```

#### Alumno:
```json
{
    "nombre": "María González",
    "correo": "maria.gonzalez@estudiante.cl",
    "fecha_ingreso": "2024-03-01"
}
```
