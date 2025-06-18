from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from sga.models.alumno import Alumno
from sga.utils.validators import ValidationError, validate_text_field, validate_email, validate_date, safe_int_conversion
from sga.utils.error_handlers import ErrorHandler, safe_form_data, validate_required_fields

alumno_bp = Blueprint('alumno', __name__)

@alumno_bp.route('/alumnos')
def listar_alumnos():
    try:
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
        
        return render_template('alumnos/listar.html', alumnos=alumnos_list)
    except Exception as e:
        flash('Error al cargar la lista de alumnos', 'error')
        return render_template('alumnos/listar.html', alumnos=[])

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

@alumno_bp.route('/alumnos/<int:id>/editar', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def editar_alumno(id):
    alumno_id = safe_int_conversion(id, 'ID del alumno')
    
    alumno_data = Alumno.get_by_id(alumno_id)
    if not alumno_data:
        raise ValidationError('Alumno no encontrado')
    
    if request.method == 'POST':
        data = safe_form_data(request.form, ['nombre', 'correo', 'fecha_ingreso'])
        
        validate_required_fields(data, ['nombre', 'correo', 'fecha_ingreso'])
        
        nombre = validate_text_field(data['nombre'], 'Nombre', min_length=2, max_length=100)
        correo = validate_email(data['correo'])
        fecha_ingreso = validate_date(data['fecha_ingreso'], 'Fecha de ingreso')
        
        Alumno.update(alumno_id, nombre, correo, fecha_ingreso)
        
        flash('Alumno actualizado exitosamente', 'success')
        return redirect(url_for('alumno.listar_alumnos'))
    
    alumno = {
        'id': alumno_data[0],
        'nombre': alumno_data[1],
        'correo': alumno_data[2],
        'fecha_ingreso': alumno_data[3]
    }
    
    return render_template('alumnos/editar.html', alumno=alumno)

@alumno_bp.route('/alumnos/<int:id>/eliminar', methods=['POST'])
@ErrorHandler.handle_route_error
def eliminar_alumno(id):
    """Elimina un alumno"""
    alumno_id = safe_int_conversion(id, 'ID del alumno')
    
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

@alumno_bp.route('/api/alumnos/<int:alumno_id>', methods=['GET'])
@ErrorHandler.handle_api_error
def get_alumno(alumno_id):
    alumno_id = safe_int_conversion(alumno_id, 'ID del alumno')
    
    alumno = Alumno.get_by_id(alumno_id)

    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    
    return jsonify({
        'id': alumno[0],
        'nombre': alumno[1],
        'correo': alumno[2],
        'fecha_ingreso': alumno[3]
    }), 200

@alumno_bp.route('/api/alumnos/<int:alumno_id>', methods=['PUT'])
@ErrorHandler.handle_api_error
def update_alumno(alumno_id):
    alumno_id = safe_int_conversion(alumno_id, 'ID del alumno')
    
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
    alumno_id = safe_int_conversion(alumno_id, 'ID del alumno')
    
    alumno_existente = Alumno.get_by_id(alumno_id)
    if not alumno_existente:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    
    Alumno.delete(alumno_id)
    return jsonify({'mensaje': 'Alumno eliminado exitosamente'}), 200
