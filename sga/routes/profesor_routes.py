from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from sga.models.profesor import Profesor
from sga.utils.validators import ValidationError, parse_integer_field
from sga.utils.error_handlers import ErrorHandler, safe_form_data

profesor_bp = Blueprint('profesor', __name__)

def _obtener_profesores_para_listado():
    """Query: Obtiene todos los profesores formateados para el listado"""
    profesores = Profesor.get_all()
    profesores_list = []
    for profesor in profesores:
        profesores_list.append({
            'id': profesor[0],
            'nombre': profesor[1],
            'correo': profesor[2]
        })
    return profesores_list

def _renderizar_listado_profesores(profesores_list):
    """Command: Renderiza la vista de listado de profesores"""
    return render_template('profesores/listar.html', profesores=profesores_list)

@profesor_bp.route('/profesores')
@ErrorHandler.handle_route_error
def listar_profesores():
    """Lista todos los profesores"""
    profesores_list = _obtener_profesores_para_listado()
    return _renderizar_listado_profesores(profesores_list)

@profesor_bp.route('/profesores/crear', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def crear_profesor():
    if request.method == 'POST':
        data = safe_form_data(request.form, ['nombre', 'correo'])
        
        Profesor.crear(data['nombre'], data['correo'])
        
        flash('Profesor creado exitosamente', 'success')
        return redirect(url_for('profesor.listar_profesores'))
    
    return render_template('profesores/crear.html')

def _obtener_profesor_por_id(profesor_id):
    """Query: Obtiene un profesor por ID y lo formatea"""
    profesor_data = Profesor.get_by_id(profesor_id)
    if not profesor_data:
        return None
    
    return {
        'id': profesor_data[0],
        'nombre': profesor_data[1],
        'correo': profesor_data[2]
    }

def _actualizar_profesor(profesor_id, data):
    """Command: Actualiza un profesor"""
    Profesor.update(profesor_id, data['nombre'], data['correo'])

def _renderizar_formulario_editar_profesor(profesor):
    """Command: Renderiza el formulario de edición de profesor"""
    return render_template('profesores/editar.html', profesor=profesor)

def _procesar_actualizacion_exitosa_profesor():
    """Command: Procesa una actualización exitosa"""
    flash('Profesor actualizado exitosamente', 'success')
    return redirect(url_for('profesor.listar_profesores'))

@profesor_bp.route('/profesores/editar/<int:profesor_id>', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def editar_profesor(profesor_id):
    profesor_id = parse_integer_field(profesor_id)
    if profesor_id is None or profesor_id <= 0:
        raise ValidationError("ID de profesor inválido")
    
    profesor = _obtener_profesor_por_id(profesor_id)
    if not profesor:
        raise ValidationError("Profesor no encontrado")
    
    if request.method == 'POST':
        data = safe_form_data(request.form, ['nombre', 'correo'])
        _actualizar_profesor(profesor_id, data)
        return _procesar_actualizacion_exitosa_profesor()
    
    return _renderizar_formulario_editar_profesor(profesor)

@profesor_bp.route('/profesores/eliminar/<int:profesor_id>', methods=['POST'])
@ErrorHandler.handle_route_error
def eliminar_profesor(profesor_id):
    profesor_id = parse_integer_field(profesor_id)
    if profesor_id is None or profesor_id <= 0:
        raise ValidationError("ID de profesor inválido")
    
    Profesor.delete(profesor_id)
    
    flash('Profesor eliminado exitosamente', 'success')
    return redirect(url_for('profesor.listar_profesores'))

def _obtener_datos_profesores_brutos():
    """Query: Obtiene datos brutos de todos los profesores"""
    return Profesor.get_all()

def _mapear_profesor_para_api(profesor_data):
    """Mapper: Mapea datos de profesor para respuesta API"""
    return {
        'id': profesor_data[0],
        'nombre': profesor_data[1],
        'correo': profesor_data[2]
    }

def _mapear_profesores_para_api(profesores_data):
    """Mapper: Mapea lista de profesores para respuesta API"""
    return [_mapear_profesor_para_api(profesor) for profesor in profesores_data]

def _crear_respuesta_profesores_exitosa(profesores_mapeados):
    """Response: Crea respuesta exitosa con lista de profesores"""
    return jsonify(profesores_mapeados)

@profesor_bp.route('/api/profesores', methods=['GET'])
@ErrorHandler.handle_api_error
def get_profesores():
    """Obtiene todos los profesores (API)"""
    profesores_data = _obtener_datos_profesores_brutos()
    profesores_mapeados = _mapear_profesores_para_api(profesores_data)
    return _crear_respuesta_profesores_exitosa(profesores_mapeados)

def _obtener_datos_profesor_por_id(profesor_id):
    """Query: Obtiene datos brutos de un profesor por ID"""
    return Profesor.get_by_id(profesor_id)

def _crear_respuesta_profesor_no_encontrado():
    """Response: Crea respuesta para profesor no encontrado"""
    return jsonify({'error': 'Profesor no encontrado'}), 404

def _crear_respuesta_profesor_exitosa(profesor_mapeado):
    """Response: Crea respuesta exitosa con datos del profesor"""
    return jsonify(profesor_mapeado)

@profesor_bp.route('/api/profesores/<int:profesor_id>', methods=['GET'])
@ErrorHandler.handle_api_error
def get_profesor(profesor_id):
    profesor_id = parse_integer_field(profesor_id)
    if profesor_id is None or profesor_id <= 0:
        raise ValidationError("ID de profesor inválido")
    
    profesor_data = _obtener_datos_profesor_por_id(profesor_id)
    if not profesor_data:
        return _crear_respuesta_profesor_no_encontrado()
    
    profesor_mapeado = _mapear_profesor_para_api(profesor_data)
    return _crear_respuesta_profesor_exitosa(profesor_mapeado)

@profesor_bp.route('/api/profesores', methods=['POST'])
@ErrorHandler.handle_api_error
def create_profesor():
    data = request.get_json()
    if not data:
        raise ValidationError("Datos JSON requeridos")
    
    if 'nombre' not in data or 'correo' not in data:
        raise ValidationError("Nombre y correo son requeridos")
    
    if not data['nombre'] or not data['correo']:
        raise ValidationError("Nombre y correo no pueden estar vacíos")
    
    Profesor.crear(data['nombre'], data['correo'])
    
    return jsonify({'mensaje': 'Profesor creado exitosamente'}), 201

@profesor_bp.route('/api/profesores/<int:profesor_id>', methods=['PUT'])
@ErrorHandler.handle_api_error
def update_profesor(profesor_id):
    profesor_id = parse_integer_field(profesor_id)
    if profesor_id is None or profesor_id <= 0:
        raise ValidationError("ID de profesor inválido")
    
    profesor_existente = Profesor.get_by_id(profesor_id)
    if not profesor_existente:
        return jsonify({'error': 'Profesor no encontrado'}), 404
    
    data = request.get_json()
    if not data:
        raise ValidationError("Datos JSON requeridos")
    
    if 'nombre' not in data or 'correo' not in data:
        raise ValidationError("Nombre y correo son requeridos")
    
    if not data['nombre'] or not data['correo']:
        raise ValidationError("Nombre y correo no pueden estar vacíos")
    
    Profesor.update(profesor_id, data['nombre'], data['correo'])
    
    return jsonify({'mensaje': 'Profesor actualizado exitosamente'}), 200

@profesor_bp.route('/api/profesores/<int:profesor_id>', methods=['DELETE'])
@ErrorHandler.handle_api_error
def delete_profesor(profesor_id):
    profesor_id = parse_integer_field(profesor_id)
    if profesor_id is None or profesor_id <= 0:
        raise ValidationError("ID de profesor inválido")
    
    profesor_existente = Profesor.get_by_id(profesor_id)
    if not profesor_existente:
        return jsonify({'error': 'Profesor no encontrado'}), 404
    
    Profesor.delete(profesor_id)
    return jsonify({'mensaje': 'Profesor eliminado exitosamente'}), 200
