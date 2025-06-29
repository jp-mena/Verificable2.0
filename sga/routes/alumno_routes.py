from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from sga.models.alumno import Alumno
from sga.utils.validators import ValidationError, validate_text_field, validate_email, validate_date, parse_integer_field
from sga.utils.error_handlers import ErrorHandler, safe_form_data, validate_required_fields

alumno_bp = Blueprint('alumno', __name__)

def _obtener_alumnos_para_listado():
    """Query: Obtiene todos los alumnos formateados para el listado"""
    alumnos = Alumno.get_all()
    alumnos_list = []
    for alumno in alumnos:
        alumno_dict = {
            'id': alumno[0],
            'nombre': alumno[1],
            'correo': alumno[2],
            'fecha_ingreso': alumno[3]
        }
        alumnos_list.append(alumno_dict)
    return alumnos_list

def _renderizar_listado_alumnos(alumnos_list):
    """Command: Renderiza la vista de listado de alumnos"""
    return render_template('alumnos/listar.html', alumnos=alumnos_list)

def _renderizar_listado_alumnos_con_error():
    """Command: Renderiza la vista de listado con error"""
    flash('Error al cargar la lista de alumnos', 'error')
    return render_template('alumnos/listar.html', alumnos=[])

@alumno_bp.route('/alumnos')
def listar_alumnos():
    try:
        alumnos_list = _obtener_alumnos_para_listado()
        return _renderizar_listado_alumnos(alumnos_list)
    except Exception:
        return _renderizar_listado_alumnos_con_error()

@alumno_bp.route('/alumnos/crear', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def crear_alumno():
    if request.method == 'POST':
        data = safe_form_data(request.form, ['nombre', 'correo', 'fecha_ingreso'])
        
        validate_required_fields(data, ['nombre', 'correo', 'fecha_ingreso'])
        
        nombre = validate_text_field(data['nombre'], 'Nombre', min_length=2, max_length=100)
        correo = validate_email(data['correo'])
        fecha_ingreso = validate_date(data['fecha_ingreso'], 'Fecha de ingreso')
        
        alumno = Alumno(nombre, correo, fecha_ingreso)
        alumno_id = alumno.save()
        
        flash('Alumno creado exitosamente', 'success')
        return redirect(url_for('alumno.listar_alumnos'))
    
    return render_template('alumnos/crear.html')

def _obtener_alumno_por_id(alumno_id):
    """Query: Obtiene un alumno por ID y lo formatea"""
    alumno_data = Alumno.get_by_id(alumno_id)
    if not alumno_data:
        return None
    
    return {
        'id': alumno_data[0],
        'nombre': alumno_data[1],
        'correo': alumno_data[2],
        'fecha_ingreso': alumno_data[3]
    }

def _actualizar_alumno_validado(alumno_id, data):
    """Command: Actualiza un alumno con datos validados"""
    validate_required_fields(data, ['nombre', 'correo', 'fecha_ingreso'])
    
    nombre = validate_text_field(data['nombre'], 'Nombre', min_length=2, max_length=100)
    correo = validate_email(data['correo'])
    fecha_ingreso = validate_date(data['fecha_ingreso'], 'Fecha de ingreso')
    
    Alumno.update(alumno_id, nombre, correo, fecha_ingreso)

def _renderizar_formulario_editar_alumno(alumno):
    """Command: Renderiza el formulario de edición de alumno"""
    return render_template('alumnos/editar.html', alumno=alumno)

def _procesar_actualizacion_exitosa_alumno():
    """Command: Procesa una actualización exitosa"""
    flash('Alumno actualizado exitosamente', 'success')
    return redirect(url_for('alumno.listar_alumnos'))

@alumno_bp.route('/alumnos/<int:id>/editar', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def editar_alumno(id):
    alumno_id = parse_integer_field(id, 'ID del alumno')
    
    alumno = _obtener_alumno_por_id(alumno_id)
    if not alumno:
        raise ValidationError('Alumno no encontrado')
    
    if request.method == 'POST':
        data = safe_form_data(request.form, ['nombre', 'correo', 'fecha_ingreso'])
        _actualizar_alumno_validado(alumno_id, data)
        return _procesar_actualizacion_exitosa_alumno()
    
    return _renderizar_formulario_editar_alumno(alumno)

@alumno_bp.route('/alumnos/<int:id>/eliminar', methods=['POST'])
@ErrorHandler.handle_route_error
def eliminar_alumno(id):
    """Elimina un alumno"""
    alumno_id = parse_integer_field(id, 'ID del alumno')
    
    alumno_data = Alumno.get_by_id(alumno_id)
    if not alumno_data:
        raise ValidationError('Alumno no encontrado')
    
    Alumno.delete(alumno_id)
    
    flash('Alumno eliminado exitosamente', 'success')
    return redirect(url_for('alumno.listar_alumnos'))

@alumno_bp.route('/api/alumnos', methods=['GET'])
@ErrorHandler.handle_api_error
def get_alumnos():
    """Obtiene todos los alumnos (API)"""
    alumnos = Alumno.get_all()
    alumnos_list = []
    for alumno in alumnos:
        alumnos_list.append({
            'id': alumno[0],
            'nombre': alumno[1],
            'correo': alumno[2],
            'fecha_ingreso': alumno[3]
        })
    return jsonify({'alumnos': alumnos_list}), 200

@alumno_bp.route('/api/alumnos', methods=['POST'])
@ErrorHandler.handle_api_error
def create_alumno():
    """Crea un nuevo alumno (API)"""
    data = request.get_json()
    if not data:
        raise ValidationError('No se recibieron datos')
    
    validate_required_fields(data, ['nombre', 'correo', 'fecha_ingreso'])
    
    nombre = validate_text_field(data['nombre'], 'Nombre', min_length=2, max_length=100)
    correo = validate_email(data['correo'])
    fecha_ingreso = validate_date(data['fecha_ingreso'], 'Fecha de ingreso')
    
    alumno = Alumno(nombre, correo, fecha_ingreso)
    alumno_id = alumno.save()
    
    return jsonify({'id': alumno_id, 'mensaje': 'Alumno creado exitosamente'}), 201

def _obtener_datos_alumno_brutos(alumno_id):
    """Query: Obtiene datos brutos del alumno"""
    return Alumno.get_by_id(alumno_id)

def _mapear_alumno_para_api(alumno_data):
    """Mapper: Mapea datos de alumno para respuesta API"""
    return {
        'id': alumno_data[0],
        'nombre': alumno_data[1],
        'correo': alumno_data[2],
        'fecha_ingreso': alumno_data[3]
    }

def _crear_respuesta_alumno_no_encontrado():
    """Response: Crea respuesta para alumno no encontrado"""
    return jsonify({'error': 'Alumno no encontrado'}), 404

def _crear_respuesta_alumno_exitosa(alumno_mapeado):
    """Response: Crea respuesta exitosa con datos del alumno"""
    return jsonify(alumno_mapeado), 200

@alumno_bp.route('/api/alumnos/<int:alumno_id>', methods=['GET'])
@ErrorHandler.handle_api_error
def get_alumno(alumno_id):
    alumno_id = parse_integer_field(alumno_id, 'ID del alumno')
    
    alumno_data = _obtener_datos_alumno_brutos(alumno_id)
    if not alumno_data:
        return _crear_respuesta_alumno_no_encontrado()
    
    alumno_mapeado = _mapear_alumno_para_api(alumno_data)
    return _crear_respuesta_alumno_exitosa(alumno_mapeado)

@alumno_bp.route('/api/alumnos/<int:alumno_id>', methods=['PUT'])
@ErrorHandler.handle_api_error
def update_alumno(alumno_id):
    alumno_id = parse_integer_field(alumno_id, 'ID del alumno')
    
    data = request.get_json()
    if not data:
        raise ValidationError('No se recibieron datos')
    
    alumno_existente = Alumno.get_by_id(alumno_id)
    if not alumno_existente:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    
    validate_required_fields(data, ['nombre', 'correo', 'fecha_ingreso'])
    
    nombre = validate_text_field(data['nombre'], 'Nombre', min_length=2, max_length=100)
    correo = validate_email(data['correo'])
    fecha_ingreso = validate_date(data['fecha_ingreso'], 'Fecha de ingreso')
    
    Alumno.update(alumno_id, nombre, correo, fecha_ingreso)
    
    return jsonify({'mensaje': 'Alumno actualizado exitosamente'}), 200

@alumno_bp.route('/api/alumnos/<int:alumno_id>', methods=['DELETE'])
@ErrorHandler.handle_api_error
def delete_alumno(alumno_id):
    alumno_id = parse_integer_field(alumno_id, 'ID del alumno')
    
    alumno_existente = Alumno.get_by_id(alumno_id)
    if not alumno_existente:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    
    Alumno.delete(alumno_id)
    return jsonify({'mensaje': 'Alumno eliminado exitosamente'}), 200
