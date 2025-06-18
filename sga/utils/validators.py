# filepath: utils/validators.py
"""
Funciones de validación para mejorar la robustez del sistema
"""
import re
from datetime import datetime

class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass

def validate_positive_integer(value, field_name="Campo"):
    """Valida que el valor sea un entero positivo"""
    if value is None:
        raise ValidationError(f"{field_name} es requerido")
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            raise ValidationError(f"{field_name} no puede estar vacío")
    
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValidationError(f"{field_name} debe ser un número positivo")
        return int_value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} debe ser un número válido")

def validate_float_range(value, min_val=1.0, max_val=7.0, field_name="Nota"):
    """Valida que el valor sea un float dentro de un rango"""
    if value is None:
        raise ValidationError(f"{field_name} es requerido")
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            raise ValidationError(f"{field_name} no puede estar vacío")
    
    try:
        float_value = float(value)
        if float_value < min_val or float_value > max_val:
            raise ValidationError(f"{field_name} debe estar entre {min_val} y {max_val}")
        return float_value
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} debe ser un número válido")

def validate_email(email, max_length=100):
    """Valida formato de email"""
    if not email or not email.strip():
        raise ValidationError("Email es requerido")
    
    email = email.strip()
    
    # Validar longitud máxima
    if len(email) > max_length:
        raise ValidationError(f"El email no puede exceder {max_length} caracteres")
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Formato de email inválido")
    
    return email

def validate_required_string(value, field_name="Campo", max_length=255):
    """Valida que el valor sea una cadena requerida no vacía"""
    if value is None:
        raise ValidationError(f"{field_name} es requerido")
    
    if isinstance(value, str):
        value = value.strip()
    else:
        value = str(value).strip()
    
    if not value:
        raise ValidationError(f"{field_name} no puede estar vacío")
    
    # Validar longitud máxima
    if len(value) > max_length:
        raise ValidationError(f"{field_name} no puede exceder {max_length} caracteres")
    
    # Validar que no contenga solo espacios o caracteres especiales
    if not re.match(r'^[a-zA-Z0-9\s\-_.,áéíóúÁÉÍÓÚñÑ]+$', value):
        raise ValidationError(f"{field_name} contiene caracteres no permitidos")
    
    return value

def validate_text_field(value, field_name="Campo", min_length=1, max_length=255):
    """Valida campos de texto"""
    if value is None:
        raise ValidationError(f"{field_name} es requerido")
    
    if isinstance(value, str):
        value = value.strip()
    else:
        value = str(value).strip()
    
    if len(value) < min_length:
        raise ValidationError(f"{field_name} debe tener al menos {min_length} caracteres")
    
    if len(value) > max_length:
        raise ValidationError(f"{field_name} no puede exceder {max_length} caracteres")
    
    return value

def validate_date(date_str, field_name="Fecha"):
    """Valida formato de fecha YYYY-MM-DD"""
    if not date_str or not date_str.strip():
        raise ValidationError(f"{field_name} es requerido")
    
    try:
        datetime.strptime(date_str.strip(), '%Y-%m-%d')
        return date_str.strip()
    except ValueError:
        raise ValidationError(f"{field_name} debe tener formato YYYY-MM-DD")

def validate_choice(value, choices, field_name="Campo"):
    """Valida que el valor esté dentro de las opciones permitidas"""
    if value not in choices:
        raise ValidationError(f"{field_name} debe ser uno de: {', '.join(map(str, choices))}")
    return value

def safe_execute_query(func, *args, **kwargs):
    """Ejecuta una función de consulta de forma segura"""
    try:
        result = func(*args, **kwargs)
        return result if result is not None else []
    except Exception as e:
        print(f"Error en consulta de base de datos: {e}")
        return []

def validate_form_data(form_data, validations):
    """
    Valida múltiples campos de un formulario
    
    Args:
        form_data: diccionario con los datos del formulario
        validations: diccionario con las reglas de validación
    
    Returns:
        diccionario con los datos validados
    
    Raises:
        ValidationError: si alguna validación falla
    """
    validated_data = {}
    
    for field_name, rules in validations.items():
        value = form_data.get(field_name)
        
        # Aplicar cada regla de validación
        for rule in rules:
            if callable(rule):
                value = rule(value)
            else:
                # Si es una tupla (función, argumentos)
                func, *args = rule if isinstance(rule, tuple) else (rule,)
                value = func(value, *args)
        
        validated_data[field_name] = value
    
    return validated_data

def safe_int_conversion(value, field_name="Campo", allow_none=False):
    """Conversión segura a entero con manejo de errores"""
    if value is None or value == '':
        if allow_none:
            return None
        raise ValidationError(f"{field_name} es requerido")
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            if allow_none:
                return None
            raise ValidationError(f"{field_name} no puede estar vacío")
    
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} debe ser un número entero válido")

def safe_float_conversion(value, field_name="Campo", allow_none=False):
    """Conversión segura a float con manejo de errores"""
    if value is None or value == '':
        if allow_none:
            return None
        raise ValidationError(f"{field_name} es requerido")
    
    if isinstance(value, str):
        value = value.strip()
        if not value:
            if allow_none:
                return None
            raise ValidationError(f"{field_name} no puede estar vacío")
    
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} debe ser un número decimal válido")

def validate_id_exists(id_value, check_function, field_name="ID", entity_name="registro"):
    """Valida que un ID exista en la base de datos"""
    try:
        id_int = safe_int_conversion(id_value, field_name)
        if not check_function(id_int):
            raise ValidationError(f"El {entity_name} seleccionado no existe")
        return id_int
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Error al validar {field_name}: {str(e)}")

def validate_percentage(value, field_name="Porcentaje"):
    """Valida que un valor sea un porcentaje válido (0-100)"""
    float_value = safe_float_conversion(value, field_name)
    if float_value < 0 or float_value > 100:
        raise ValidationError(f"{field_name} debe estar entre 0 y 100")
    return float_value

def validate_semester(value, field_name="Semestre"):
    """Valida que el semestre sea 1 o 2"""
    int_value = safe_int_conversion(value, field_name)
    if int_value not in [1, 2]:
        raise ValidationError(f"{field_name} debe ser 1 o 2")
    return int_value

def validate_year(value, field_name="Año", min_year=2000, max_year=2030):
    """Valida que el año esté en un rango razonable"""
    int_value = safe_int_conversion(value, field_name)
    if int_value < min_year or int_value > max_year:
        raise ValidationError(f"{field_name} debe estar entre {min_year} y {max_year}")
    return int_value

def handle_database_error(func):
    """Decorator para manejar errores de base de datos de forma consistente"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error en operación de base de datos: {e}")
            raise ValidationError(f"Error en la operación: {str(e)}")
    return wrapper
