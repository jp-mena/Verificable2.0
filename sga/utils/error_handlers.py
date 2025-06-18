# filepath: utils/error_handlers.py
"""
Sistema centralizado de manejo de errores para el SGA
"""
import logging
import traceback
from functools import wraps
from flask import flash, redirect, url_for, request, jsonify
from sga.utils.validators import ValidationError

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Clase para manejo centralizado de errores"""
    
    @staticmethod
    def handle_route_error(func):
        """Decorator para manejo de errores en rutas"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.warning(f"Error de validación en {func.__name__}: {e}")
                flash(str(e), 'error')
                # Redirigir a la página anterior o a la lista principal
                return ErrorHandler._get_safe_redirect(func.__name__)
            except Exception as e:
                logger.error(f"Error inesperado en {func.__name__}: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.error(f"Request args: {request.args}")
                logger.error(f"Request form: {request.form}")                
                flash('Ha ocurrido un error inesperado. Por favor, intente nuevamente.', 'error')
                return ErrorHandler._get_safe_redirect(func.__name__)
        return wrapper
    
    @staticmethod
    def handle_api_error(func):
        """Decorator para manejo de errores en APIs"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.warning(f"Error de validación en API {func.__name__}: {e}")
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                logger.error(f"Error inesperado en API {func.__name__}: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return jsonify({'error': 'Error interno del servidor'}), 500
        return wrapper
    
    @staticmethod
    def _get_safe_redirect(func_name):
        """Obtiene una redirección segura basada en el nombre de la función"""
        # Mapeo de funciones a rutas de listado
        route_map = {
            'crear_alumno': 'alumno.listar_alumnos',
            'editar_alumno': 'alumno.listar_alumnos',
            'eliminar_alumno': 'alumno.listar_alumnos',
            'crear_curso': 'curso.listar_cursos',
            'editar_curso': 'curso.listar_cursos',
            'eliminar_curso': 'curso.listar_cursos',
            'crear_instancia': 'instancia_curso.listar_instancias',
            'editar_instancia': 'instancia_curso.listar_instancias',
            'eliminar_instancia': 'instancia_curso.listar_instancias',
            'cerrar_instancia': 'instancia_curso.listar_instancias',
            'inscribir_alumno': 'instancia_curso.listar_instancias',
            'desinscribir_alumno': 'instancia_curso.listar_instancias',
            'crear_evaluacion': 'evaluacion.listar_evaluaciones',
            'editar_evaluacion': 'evaluacion.listar_evaluaciones',
            'eliminar_evaluacion': 'evaluacion.listar_evaluaciones',
            'crear_topico': 'topico.listar_topicos',
            'editar_topico': 'topico.listar_topicos',
            'eliminar_topico': 'topico.listar_topicos',
            'crear_instancia_topico': 'instancia_topico.listar_instancias',
            'editar_instancia_topico': 'instancia_topico.listar_instancias',
            'eliminar_instancia_topico': 'instancia_topico.listar_instancias',
            'crear_nota': 'nota.listar_notas',
            'editar_nota': 'nota.listar_notas',
            'eliminar_nota': 'nota.listar_notas',
            'crear_profesor': 'profesor.listar_profesores',
            'editar_profesor': 'profesor.listar_profesores',
            'eliminar_profesor': 'profesor.listar_profesores',
            'crear_seccion': 'seccion.listar_secciones',
            'editar_seccion': 'seccion.listar_secciones',
            'eliminar_seccion': 'seccion.listar_secciones',
        }
        
        # Intentar obtener la ruta específica
        if func_name in route_map:
            return redirect(url_for(route_map[func_name]))
        
        # Fallback a la página principal
        return redirect(url_for('index'))

def safe_form_data(form, fields):
    """Extrae datos del formulario de forma segura"""
    data = {}
    for field in fields:
        value = form.get(field, '').strip() if form.get(field) else ''
        data[field] = value
    return data

def validate_required_fields(data, required_fields):
    """Valida que todos los campos requeridos estén presentes"""
    for field in required_fields:
        if not data.get(field):
            raise ValidationError(f"El campo '{field}' es requerido")

def safe_database_operation(operation, *args, **kwargs):
    """Ejecuta una operación de base de datos de forma segura"""
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        print(f"Error en operación de base de datos: {e}")
        raise ValidationError(f"Error en la operación: {str(e)}")

def format_error_message(error, context=""):
    """Formatea mensajes de error de forma consistente"""
    if isinstance(error, ValidationError):
        return str(error)
    else:
        print(f"Error inesperado {context}: {error}")
        return "Ha ocurrido un error inesperado. Por favor, intente nuevamente."
