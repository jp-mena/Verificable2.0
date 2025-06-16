# Tests del Sistema SGA

Esta carpeta contiene todos los archivos de testing del sistema SGA.

## Archivos de Testing

### 🧪 **test_error_handling.py**
Pruebas de robustez del sistema contra datos inválidos y maliciosos.
```bash
python tests/test_error_handling.py
```

### 🔄 **test_nuevos_cruds.py**
Pruebas de las operaciones CRUD de todas las entidades.
```bash
python tests/test_nuevos_cruds.py
```

### 📊 **test_reportes.py**
Pruebas de la funcionalidad de reportes del sistema.
```bash
python tests/test_reportes.py
```

### 🚀 **test_nuevas_funcionalidades.py**
Pruebas de las nuevas funcionalidades implementadas.
```bash
python tests/test_nuevas_funcionalidades.py
```

### 📁 **test_carga_json.py**
Pruebas de carga de datos desde archivos JSON.
```bash
python tests/test_carga_json.py
```

## Cómo ejecutar todos los tests

```bash
# Desde la raíz del proyecto
python -m pytest tests/

# O ejecutar individualmente
python tests/test_error_handling.py
python tests/test_nuevos_cruds.py
python tests/test_reportes.py
python tests/test_nuevas_funcionalidades.py
python tests/test_carga_json.py
```

## Requisitos

Asegúrate de que la base de datos esté inicializada antes de ejecutar los tests:

```bash
python app.py  # Esto inicializa la BD automáticamente
```
