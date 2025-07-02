from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from sga.models.curso import Curso
from sga.utils.validators import ValidationError, validate_text_field, parse_integer_field
from sga.utils.error_handlers import ErrorHandler, safe_form_data, validate_required_fields

curso_bp = Blueprint('curso', __name__)

def _obtener_cursos_para_listado():
    cursos = Curso.get_all()
    cursos_list = []
    for curso in cursos:
        cursos_list.append({
            'id': getattr(curso, 'id', None),
            'codigo': curso.codigo,
            'nombre': curso.nombre,
            'creditos': curso.creditos,
            'requisitos': curso.requisitos if curso.requisitos else ''
        })
    return cursos_list

def _renderizar_listado_cursos(cursos_list):
    return render_template('cursos/listar.html', cursos=cursos_list)

def _renderizar_listado_cursos_con_error():
    flash('Error al cargar la lista de cursos', 'error')
    return render_template('cursos/listar.html', cursos=[])

@curso_bp.route('/cursos')
def listar_cursos():
    try:
        cursos_list = _obtener_cursos_para_listado()
        return _renderizar_listado_cursos(cursos_list)
    except Exception as e:
        return _renderizar_listado_cursos_con_error()

@curso_bp.route('/cursos/crear', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def crear_curso():
    if request.method == 'POST':
        data = safe_form_data(request.form, ['codigo', 'nombre', 'creditos'])
        
        validate_required_fields(data, ['codigo', 'nombre', 'creditos'])
        
        codigo = validate_text_field(data['codigo'], 'Código', min_length=3, max_length=20)
        nombre = validate_text_field(data['nombre'], 'Nombre', min_length=3, max_length=100)
        creditos = parse_integer_field(data['creditos'], 'Créditos')
        if creditos is None or creditos < 1 or creditos > 12:
            raise ValidationError("Los créditos deben ser un número entre 1 y 12")
        
        requisitos_list = request.form.getlist('requisitos')
        
        if requisitos_list:
            Curso.validate_requisitos(requisitos_list, codigo)
        
        curso = Curso(codigo, nombre, creditos, requisitos_list)
        curso_id = curso.save()
        
        flash('Curso creado exitosamente', 'success')
        return redirect(url_for('curso.listar_cursos'))
    
    cursos_disponibles = Curso.get_prerequisitos_disponibles()
    return render_template('cursos/crear.html', cursos_disponibles=cursos_disponibles)

@curso_bp.route('/cursos/<int:id>/editar', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def editar_curso(id):
    curso_data = _validar_curso_existente(id)
    
    if request.method == 'POST':
        return _procesar_edicion_curso(curso_data)
    
    return _mostrar_formulario_edicion(curso_data)

def _validar_curso_existente(id):
    curso_id = parse_integer_field(id, 'ID del curso')
    curso_data = Curso.get_by_id(curso_id)
    if not curso_data:
        raise ValidationError('Curso no encontrado')
    return curso_data

def _procesar_edicion_curso(curso_data):
    datos_validados = _validar_datos_formulario_edicion()
    _actualizar_curso_con_datos(curso_data, datos_validados)
    
    flash('Curso actualizado exitosamente', 'success')
    return redirect(url_for('curso.listar_cursos'))

def _validar_datos_formulario_edicion():
    data = safe_form_data(request.form, ['codigo', 'nombre', 'creditos'])
    validate_required_fields(data, ['codigo', 'nombre', 'creditos'])
    
    codigo = validate_text_field(data['codigo'], 'Código', min_length=3, max_length=20)
    nombre = validate_text_field(data['nombre'], 'Nombre', min_length=3, max_length=100)
    creditos = _validar_creditos(data['creditos'])
    requisitos_list = request.form.getlist('requisitos')
    
    if requisitos_list:
        Curso.validate_requisitos(requisitos_list, codigo)
    
    return {
        'codigo': codigo,
        'nombre': nombre,
        'creditos': creditos,
        'requisitos_list': requisitos_list
    }

def _validar_creditos(creditos_str):
    creditos = parse_integer_field(creditos_str, 'Créditos')
    if creditos is None or creditos < 1 or creditos > 12:
        raise ValidationError("Los créditos deben ser un número entre 1 y 12")
    return creditos

def _actualizar_curso_con_datos(curso_data, datos_validados):
    curso_data.codigo = datos_validados['codigo']
    curso_data.nombre = datos_validados['nombre']
    curso_data.creditos = datos_validados['creditos']
    curso_data.requisitos = curso_data._process_requisitos(datos_validados['requisitos_list'])
    curso_data.update()

def _mostrar_formulario_edicion(curso_data):
    curso = _convertir_curso_a_diccionario(curso_data)
    cursos_disponibles = _obtener_cursos_disponibles_edicion(curso['codigo'])
    requisitos_actuales = Curso.get_requisitos_as_list(curso['requisitos'])
    
    return render_template('cursos/editar.html', 
                         curso=curso, 
                         cursos_disponibles=cursos_disponibles, 
                         requisitos_actuales=requisitos_actuales)

def _convertir_curso_a_diccionario(curso_data):
    return {
        'id': curso_data.id if hasattr(curso_data, 'id') else None,
        'codigo': curso_data.codigo,
        'nombre': curso_data.nombre,
        'creditos': curso_data.creditos,
        'requisitos': curso_data.requisitos if curso_data.requisitos else ''
    }

def _obtener_cursos_disponibles_edicion(codigo_actual):
    todos_los_cursos = Curso.get_prerequisitos_disponibles()
    return [c for c in todos_los_cursos if c['codigo'] != codigo_actual]

@curso_bp.route('/cursos/<int:id>/eliminar', methods=['POST'])
@ErrorHandler.handle_route_error
def eliminar_curso(id):
    curso_id = parse_integer_field(id, 'ID del curso')
    
    curso_data = Curso.get_by_id(curso_id)
    if not curso_data:
        raise ValidationError('Curso no encontrado')
    
    Curso.delete(curso_id)
    
    flash('Curso eliminado exitosamente', 'success')
    return redirect(url_for('curso.listar_cursos'))

@curso_bp.route('/api/cursos', methods=['GET'])
@ErrorHandler.handle_api_error
def get_cursos():
    cursos = Curso.get_all()
    cursos_list = []
    for curso in cursos:
        cursos_list.append({
            'id': getattr(curso, 'id', None),
            'codigo': curso.codigo,
            'nombre': curso.nombre,
            'requisitos': curso.requisitos
        })
    return jsonify({'cursos': cursos_list}), 200

@curso_bp.route('/api/cursos', methods=['POST'])
@ErrorHandler.handle_api_error
def create_curso():
    data = request.get_json()
    if not data:
        raise ValidationError('No se recibieron datos')
    
    validate_required_fields(data, ['codigo', 'nombre'])
    
    codigo = validate_text_field(data['codigo'], 'Código', min_length=3, max_length=20)
    nombre = validate_text_field(data['nombre'], 'Nombre', min_length=3, max_length=100)
    requisitos = data.get('requisitos')
    
    if requisitos:
        requisitos = validate_text_field(requisitos, 'Requisitos', min_length=0, max_length=500)
    
    curso = Curso(codigo, nombre, requisitos)
    curso_id = curso.save()
    
    return jsonify({'id': curso_id, 'mensaje': 'Curso creado exitosamente'}), 201

@curso_bp.route('/api/cursos/<int:curso_id>', methods=['GET'])
@ErrorHandler.handle_api_error
def get_curso(curso_id):
    curso_id = parse_integer_field(curso_id, 'ID del curso')
    
    curso = Curso.get_by_id(curso_id)
    if not curso:
        return jsonify({'error': 'Curso no encontrado'}), 404
    
    return jsonify({
        'id': curso[0],
        'codigo': curso[1],
        'nombre': curso[2],
        'requisitos': curso[3]
    }), 200

@curso_bp.route('/api/cursos/<int:curso_id>', methods=['PUT'])
@ErrorHandler.handle_api_error
def update_curso(curso_id):
    curso_id = parse_integer_field(curso_id, 'ID del curso')
    
    data = request.get_json()
    if not data:
        raise ValidationError('No se recibieron datos')
    
    curso_existente = Curso.get_by_id(curso_id)
    if not curso_existente:
        return jsonify({'error': 'Curso no encontrado'}), 404
    
    validate_required_fields(data, ['codigo', 'nombre'])
    
    codigo = validate_text_field(data['codigo'], 'Código', min_length=3, max_length=20)
    nombre = validate_text_field(data['nombre'], 'Nombre', min_length=3, max_length=100)
    requisitos = data.get('requisitos')
    
    if requisitos:
        requisitos = validate_text_field(requisitos, 'Requisitos', min_length=0, max_length=500)
    
    Curso.update(curso_id, codigo, nombre, requisitos)
    
    return jsonify({'mensaje': 'Curso actualizado exitosamente'}), 200

@curso_bp.route('/api/cursos/<int:curso_id>', methods=['DELETE'])
@ErrorHandler.handle_api_error
def delete_curso(curso_id):
    curso_id = parse_integer_field(curso_id, 'ID del curso')
    
    curso_existente = Curso.get_by_id(curso_id)
    if not curso_existente:
        return jsonify({'error': 'Curso no encontrado'}), 404
    
    Curso.delete(curso_id)
    return jsonify({'mensaje': 'Curso eliminado exitosamente'}), 200
