# filepath: routes/profesor_routes.py
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from sga.models.profesor import Profesor
from sga.utils.validators import ValidationError, safe_int_conversion
from sga.utils.error_handlers import ErrorHandler, safe_form_data

profesor_bp = Blueprint('profesor', __name__)

@profesor_bp.route('/profesores')
@ErrorHandler.handle_route_error
def listar_profesores():
    """Lista todos los profesores"""
    profesores = Profesor.get_all()
    profesores_list = []
    for profesor in profesores:
        profesores_list.append({
            'id': profesor[0],
            'nombre': profesor[1],
            'correo': profesor[2]
        })
    return render_template('profesores/listar.html', profesores=profesores_list)

@profesor_bp.route('/profesores/crear', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def crear_profesor():
    """Crea un nuevo profesor"""
    if request.method == 'POST':
        # Extraer y validar datos del formulario
        data = safe_form_data(request.form, ['nombre', 'correo'])
        
        # Crear profesor usando el modelo robusto
        Profesor.crear(data['nombre'], data['correo'])
        
        flash('Profesor creado exitosamente', 'success')
        return redirect(url_for('profesor.listar_profesores'))
    
    return render_template('profesores/crear.html')

@profesor_bp.route('/profesores/editar/<int:profesor_id>', methods=['GET', 'POST'])
@ErrorHandler.handle_route_error
def editar_profesor(profesor_id):
    """Edita un profesor existente"""
    # Validar ID
    profesor_id = safe_int_conversion(profesor_id)
    if profesor_id is None or profesor_id <= 0:
        raise ValidationError("ID de profesor inválido")
    
    # Verificar que el profesor existe
    profesor_data = Profesor.get_by_id(profesor_id)
    if not profesor_data:
        raise ValidationError("Profesor no encontrado")
    
    if request.method == 'POST':
        # Extraer y validar datos del formulario
        data = safe_form_data(request.form, ['nombre', 'correo'])
        
        # Actualizar profesor
        Profesor.update(profesor_id, data['nombre'], data['correo'])
        
        flash('Profesor actualizado exitosamente', 'success')
        return redirect(url_for('profesor.listar_profesores'))
    
    # Para GET, mostrar formulario con datos actuales
    profesor = {
        'id': profesor_data[0],
        'nombre': profesor_data[1],
        'correo': profesor_data[2]
    }
    return render_template('profesores/editar.html', profesor=profesor)

@profesor_bp.route('/profesores/eliminar/<int:profesor_id>', methods=['POST'])
@ErrorHandler.handle_route_error
def eliminar_profesor(profesor_id):
    """Elimina un profesor"""
    # Validar ID
    profesor_id = safe_int_conversion(profesor_id)
    if profesor_id is None or profesor_id <= 0:
        raise ValidationError("ID de profesor inválido")
    
    # Eliminar usando el método robusto del modelo
    Profesor.delete(profesor_id)
    
    flash('Profesor eliminado exitosamente', 'success')
    return redirect(url_for('profesor.listar_profesores'))

# API Routes
@profesor_bp.route('/api/profesores', methods=['GET'])
@ErrorHandler.handle_api_error
def get_profesores():
    """Obtiene todos los profesores (API)"""
    profesores = Profesor.get_all()
    profesores_list = []
    for profesor in profesores:
        profesores_list.append({
            'id': profesor[0],
            'nombre': profesor[1],
            'correo': profesor[2]
        })
    return jsonify(profesores_list)

@profesor_bp.route('/api/profesores/<int:profesor_id>', methods=['GET'])
@ErrorHandler.handle_api_error
def get_profesor(profesor_id):
    """Obtiene un profesor específico (API)"""
    # Validar ID
    profesor_id = safe_int_conversion(profesor_id)
    if profesor_id is None or profesor_id <= 0:
        raise ValidationError("ID de profesor inválido")
    
    profesor_data = Profesor.get_by_id(profesor_id)
    if not profesor_data:
        return jsonify({'error': 'Profesor no encontrado'}), 404
    
    profesor = {
        'id': profesor_data[0],
        'nombre': profesor_data[1],
        'correo': profesor_data[2]
    }
    return jsonify(profesor)

@profesor_bp.route('/api/profesores', methods=['POST'])
@ErrorHandler.handle_api_error
def create_profesor():
    """Crea un nuevo profesor (API)"""
    data = request.get_json()
    if not data:
        raise ValidationError("Datos JSON requeridos")
    
    # Validar campos requeridos
    if 'nombre' not in data or 'correo' not in data:
        raise ValidationError("Nombre y correo son requeridos")
    
    if not data['nombre'] or not data['correo']:
        raise ValidationError("Nombre y correo no pueden estar vacíos")
    
    # Crear profesor usando el modelo robusto
    Profesor.crear(data['nombre'], data['correo'])
    
    return jsonify({'mensaje': 'Profesor creado exitosamente'}), 201

@profesor_bp.route('/api/profesores/<int:profesor_id>', methods=['PUT'])
@ErrorHandler.handle_api_error
def update_profesor(profesor_id):
    """Actualiza un profesor específico (API)"""
    # Validar ID
    profesor_id = safe_int_conversion(profesor_id)
    if profesor_id is None or profesor_id <= 0:
        raise ValidationError("ID de profesor inválido")
    
    # Verificar que el profesor existe
    profesor_existente = Profesor.get_by_id(profesor_id)
    if not profesor_existente:
        return jsonify({'error': 'Profesor no encontrado'}), 404
    
    data = request.get_json()
    if not data:
        raise ValidationError("Datos JSON requeridos")
    
    # Validar campos requeridos
    if 'nombre' not in data or 'correo' not in data:
        raise ValidationError("Nombre y correo son requeridos")
    
    if not data['nombre'] or not data['correo']:
        raise ValidationError("Nombre y correo no pueden estar vacíos")
    
    # Actualizar profesor
    Profesor.update(profesor_id, data['nombre'], data['correo'])
    
    return jsonify({'mensaje': 'Profesor actualizado exitosamente'}), 200

@profesor_bp.route('/api/profesores/<int:profesor_id>', methods=['DELETE'])
@ErrorHandler.handle_api_error
def delete_profesor(profesor_id):
    """Elimina un profesor específico (API)"""
    # Validar ID
    profesor_id = safe_int_conversion(profesor_id)
    if profesor_id is None or profesor_id <= 0:
        raise ValidationError("ID de profesor inválido")
    
    profesor_existente = Profesor.get_by_id(profesor_id)
    if not profesor_existente:
        return jsonify({'error': 'Profesor no encontrado'}), 404
    
    Profesor.delete(profesor_id)
    return jsonify({'mensaje': 'Profesor eliminado exitosamente'}), 200
