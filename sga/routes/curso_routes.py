# filepath: routes/curso_routes.py
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from sga.models.curso import Curso
from sga.utils.validators import ValidationError, validate_text_field, safe_int_conversion
from sga.utils.error_handlers import ErrorHandler, safe_form_data, validate_required_fields

curso_bp = Blueprint('curso', __name__)

@curso_bp.route('/cursos')
def listar_cursos():
    """Lista todos los cursos"""
    try:
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
        return render_template('cursos/listar.html', cursos=cursos_list)
    except Exception as e:
        flash('Error al cargar la lista de cursos', 'error')
        return render_template('cursos/listar.html', cursos=[])

@curso_bp.route('/cursos/crear', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def crear_curso():
    """Crea un nuevo curso"""
    if request.method == 'POST':
        # Extraer datos del formulario de forma segura
        data = safe_form_data(request.form, ['codigo', 'nombre', 'creditos'])
        
        # Validar campos requeridos
        validate_required_fields(data, ['codigo', 'nombre', 'creditos'])
        
        # Validar formato de cada campo
        codigo = validate_text_field(data['codigo'], 'Código', min_length=3, max_length=20)
        nombre = validate_text_field(data['nombre'], 'Nombre', min_length=3, max_length=100)
        creditos = safe_int_conversion(data['creditos'], 'Créditos')
        if creditos is None or creditos < 1 or creditos > 12:
            raise ValidationError("Los créditos deben ser un número entre 1 y 12")
        
        # Obtener requisitos seleccionados (pueden ser múltiples)
        requisitos_list = request.form.getlist('requisitos')
        
        # Validar requisitos
        if requisitos_list:
            Curso.validate_requisitos(requisitos_list, codigo)
        
        # Crear el curso
        curso = Curso(codigo, nombre, creditos, requisitos_list)
        curso_id = curso.save()
        
        flash('Curso creado exitosamente', 'success')
        return redirect(url_for('curso.listar_cursos'))
    
    # Para GET, obtener cursos disponibles como prerrequisitos
    cursos_disponibles = Curso.get_prerequisitos_disponibles()
    return render_template('cursos/crear.html', cursos_disponibles=cursos_disponibles)

@curso_bp.route('/cursos/<int:id>/editar', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def editar_curso(id):
    """Edita un curso existente"""
    # Validar que el ID sea válido
    curso_id = safe_int_conversion(id, 'ID del curso')
    
    # Verificar que el curso existe
    curso_data = Curso.get_by_id(curso_id)
    if not curso_data:
        raise ValidationError('Curso no encontrado')
    
    if request.method == 'POST':
        # Extraer datos del formulario de forma segura
        data = safe_form_data(request.form, ['codigo', 'nombre', 'creditos'])
        
        # Validar campos requeridos
        validate_required_fields(data, ['codigo', 'nombre', 'creditos'])
        
        # Validar formato de cada campo
        codigo = validate_text_field(data['codigo'], 'Código', min_length=3, max_length=20)
        nombre = validate_text_field(data['nombre'], 'Nombre', min_length=3, max_length=100)
        creditos = safe_int_conversion(data['creditos'], 'Créditos')
        if creditos is None or creditos < 1 or creditos > 12:
            raise ValidationError("Los créditos deben ser un número entre 1 y 12")
        
        # Obtener requisitos seleccionados (pueden ser múltiples)
        requisitos_list = request.form.getlist('requisitos')
        
        # Validar requisitos (no puede ser prerrequisito de sí mismo)
        if requisitos_list:
            Curso.validate_requisitos(requisitos_list, codigo)
        
        # Actualizar el curso
        Curso.update(curso_id, codigo, nombre, creditos, requisitos_list)
        
        flash('Curso actualizado exitosamente', 'success')
        return redirect(url_for('curso.listar_cursos'))
      # Convertir objeto a diccionario para la plantilla
    curso = {
        'id': curso_data.id if hasattr(curso_data, 'id') else None,
        'codigo': curso_data.codigo,
        'nombre': curso_data.nombre,
        'creditos': curso_data.creditos,
        'requisitos': curso_data.requisitos if curso_data.requisitos else ''
    }
      # Obtener cursos disponibles (igual que en crear) pero filtrar el curso actual
    todos_los_cursos = Curso.get_prerequisitos_disponibles()
    cursos_disponibles = [c for c in todos_los_cursos if c['codigo'] != curso['codigo']]
    requisitos_actuales = Curso.get_requisitos_as_list(curso['requisitos'])
    
    return render_template('cursos/editar.html', curso=curso, 
                         cursos_disponibles=cursos_disponibles, 
                         requisitos_actuales=requisitos_actuales)

@curso_bp.route('/cursos/<int:id>/eliminar', methods=['POST'])
@ErrorHandler.handle_route_error
def eliminar_curso(id):
    """Elimina un curso"""
    # Validar que el ID sea válido
    curso_id = safe_int_conversion(id, 'ID del curso')
    
    # Verificar que el curso existe
    curso_data = Curso.get_by_id(curso_id)
    if not curso_data:
        raise ValidationError('Curso no encontrado')
    
    # TODO: Verificar que no haya instancias de curso asociadas
    # before deleting (agregar validación de relaciones)
    
    # Eliminar el curso
    Curso.delete(curso_id)
    
    flash('Curso eliminado exitosamente', 'success')
    return redirect(url_for('curso.listar_cursos'))

# API endpoints (mantenidos para compatibilidad)
@curso_bp.route('/api/cursos', methods=['GET'])
@ErrorHandler.handle_api_error
def get_cursos():
    """Obtiene todos los cursos (API)"""
    cursos = Curso.get_all()
    cursos_list = []
    for curso in cursos:
        cursos_list.append({
            'id': curso[0],
            'codigo': curso[1],
            'nombre': curso[2],
            'requisitos': curso[3]
        })
    return jsonify({'cursos': cursos_list}), 200

@curso_bp.route('/api/cursos', methods=['POST'])
@ErrorHandler.handle_api_error
def create_curso():
    """Crea un nuevo curso (API)"""
    data = request.get_json()
    if not data:
        raise ValidationError('No se recibieron datos')
    
    # Validar campos requeridos
    validate_required_fields(data, ['codigo', 'nombre'])
    
    # Validar formato de cada campo
    codigo = validate_text_field(data['codigo'], 'Código', min_length=3, max_length=20)
    nombre = validate_text_field(data['nombre'], 'Nombre', min_length=3, max_length=100)
    requisitos = data.get('requisitos')
    
    if requisitos:
        requisitos = validate_text_field(requisitos, 'Requisitos', min_length=0, max_length=500)
    
    # Crear el curso
    curso = Curso(codigo, nombre, requisitos)
    curso_id = curso.save()
    
    return jsonify({'id': curso_id, 'mensaje': 'Curso creado exitosamente'}), 201

@curso_bp.route('/api/cursos/<int:curso_id>', methods=['GET'])
@ErrorHandler.handle_api_error
def get_curso(curso_id):
    """Obtiene un curso específico (API)"""
    # Validar que el ID sea válido
    curso_id = safe_int_conversion(curso_id, 'ID del curso')
    
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
    """Actualiza un curso específico (API)"""
    # Validar que el ID sea válido
    curso_id = safe_int_conversion(curso_id, 'ID del curso')
    
    data = request.get_json()
    if not data:
        raise ValidationError('No se recibieron datos')
    
    # Verificar que el curso existe
    curso_existente = Curso.get_by_id(curso_id)
    if not curso_existente:
        return jsonify({'error': 'Curso no encontrado'}), 404
    
    # Validar campos requeridos
    validate_required_fields(data, ['codigo', 'nombre'])
    
    # Validar formato de cada campo
    codigo = validate_text_field(data['codigo'], 'Código', min_length=3, max_length=20)
    nombre = validate_text_field(data['nombre'], 'Nombre', min_length=3, max_length=100)
    requisitos = data.get('requisitos')
    
    if requisitos:
        requisitos = validate_text_field(requisitos, 'Requisitos', min_length=0, max_length=500)
    
    # Actualizar el curso
    Curso.update(curso_id, codigo, nombre, requisitos)
    
    return jsonify({'mensaje': 'Curso actualizado exitosamente'}), 200

@curso_bp.route('/api/cursos/<int:curso_id>', methods=['DELETE'])
@ErrorHandler.handle_api_error
def delete_curso(curso_id):
    """Elimina un curso específico (API)"""
    # Validar que el ID sea válido
    curso_id = safe_int_conversion(curso_id, 'ID del curso')
    
    curso_existente = Curso.get_by_id(curso_id)
    if not curso_existente:
        return jsonify({'error': 'Curso no encontrado'}), 404
    
    Curso.delete(curso_id)
    return jsonify({'mensaje': 'Curso eliminado exitosamente'}), 200
