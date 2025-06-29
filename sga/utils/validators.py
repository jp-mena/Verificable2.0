import re
from datetime import datetime

class ValidationError(Exception):
    pass

def validate_positive_integer(value, field_name="Campo"):
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
    if value is None:
        raise ValidationError(f"{field_name} es requerido")
    
    if isinstance(value, str):
        value = value.strip()
    else:
        value = str(value).strip()
    
    if not value:
        raise ValidationError(f"{field_name} no puede estar vacío")
    
    if len(value) > max_length:
        raise ValidationError(f"{field_name} no puede exceder {max_length} caracteres")
    
    if not re.match(r'^[a-zA-Z0-9\s\-_.,áéíóúÁÉÍÓÚñÑ]+$', value):
        raise ValidationError(f"{field_name} contiene caracteres no permitidos")
    
    return value

def validate_text_field(value, field_name="Campo", min_length=1, max_length=255):
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
    if not date_str or not date_str.strip():
        raise ValidationError(f"{field_name} es requerido")
    
    try:
        datetime.strptime(date_str.strip(), '%Y-%m-%d')
        return date_str.strip()
    except ValueError:
        raise ValidationError(f"{field_name} debe tener formato YYYY-MM-DD")

def validate_choice(value, choices, field_name="Campo"):
    if value not in choices:
        raise ValidationError(f"{field_name} debe ser uno de: {', '.join(map(str, choices))}")
    return value

def safe_execute_query(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        return result if result is not None else []
    except Exception as e:
        print(f"Error en consulta de base de datos: {e}")
        return []

def validate_form_data(form_data, validations):

    validated_data = {}
    
    for field_name, rules in validations.items():
        value = form_data.get(field_name)
        
        for rule in rules:
            if callable(rule):
                value = rule(value)
            else:
                func, *args = rule if isinstance(rule, tuple) else (rule,)
                value = func(value, *args)
        
        validated_data[field_name] = value
    
    return validated_data

def parse_integer_field(value, field_name="Campo", allow_none=False):
    """
    Convierte un valor a entero validando el formato y nulidad.
    
    Args:
        value: Valor a convertir
        field_name: Nombre del campo para mensajes de error
        allow_none: Si permite valores nulos
        
    Returns:
        int: Valor convertido a entero o None si se permite
        
    Raises:
        ValidationError: Si el valor no es convertible o está vacío cuando no se permite
    """
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

def parse_decimal_field(value, field_name="Campo", allow_none=False):
    """
    Convierte un valor a decimal validando el formato y nulidad.
    
    Args:
        value: Valor a convertir
        field_name: Nombre del campo para mensajes de error
        allow_none: Si permite valores nulos
        
    Returns:
        float: Valor convertido a decimal o None si se permite
        
    Raises:
        ValidationError: Si el valor no es convertible o está vacío cuando no se permite
    """
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
    try:
        id_int = parse_integer_field(id_value, field_name)
        if not check_function(id_int):
            raise ValidationError(f"El {entity_name} seleccionado no existe")
        return id_int
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Error al validar {field_name}: {str(e)}")

def validate_percentage(value, field_name="Porcentaje"):
    float_value = parse_decimal_field(value, field_name)
    if float_value < 0 or float_value > 100:
        raise ValidationError(f"{field_name} debe estar entre 0 y 100")
    return float_value

def validate_semester(value, field_name="Semestre"):
    int_value = parse_integer_field(value, field_name)
    if int_value not in [1, 2]:
        raise ValidationError(f"{field_name} debe ser 1 o 2")
    return int_value

def validate_year(value, field_name="Año", min_year=2000, max_year=2030):
    int_value = parse_integer_field(value, field_name)
    if int_value < min_year or int_value > max_year:
        raise ValidationError(f"{field_name} debe estar entre {min_year} y {max_year}")
    return int_value

def handle_database_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error en operación de base de datos: {e}")
            raise ValidationError(f"Error en la operación: {str(e)}")
    return wrapper
