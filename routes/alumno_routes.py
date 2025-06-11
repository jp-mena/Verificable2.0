from flask import Blueprint, request, jsonify
from models.alumno import Alumno

alumno_bp = Blueprint('alumno', __name__)

@alumno_bp.route('/alumnos', methods=['GET'])
def get_alumnos():
    """Obtiene todos los alumnos"""
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alumno_bp.route('/alumnos', methods=['POST'])
def create_alumno():
    """Crea un nuevo alumno"""
    try:
        data = request.get_json()
        if not data or 'nombre' not in data or 'correo' not in data or 'fecha_ingreso' not in data:
            return jsonify({'error': 'Nombre, correo y fecha de ingreso son requeridos'}), 400
        
        alumno = Alumno(data['nombre'], data['correo'], data['fecha_ingreso'])
        alumno_id = alumno.save()
        return jsonify({'id': alumno_id, 'mensaje': 'Alumno creado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alumno_bp.route('/alumnos/<int:alumno_id>', methods=['GET'])
def get_alumno(alumno_id):
    """Obtiene un alumno específico"""
    try:
        alumno = Alumno.get_by_id(alumno_id)
        if not alumno:
            return jsonify({'error': 'Alumno no encontrado'}), 404
        
        return jsonify({
            'id': alumno[0],
            'nombre': alumno[1],
            'correo': alumno[2],
            'fecha_ingreso': alumno[3]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alumno_bp.route('/alumnos/<int:alumno_id>', methods=['PUT'])
def update_alumno(alumno_id):
    """Actualiza un alumno específico"""
    try:
        data = request.get_json()
        if not data or 'nombre' not in data or 'correo' not in data or 'fecha_ingreso' not in data:
            return jsonify({'error': 'Nombre, correo y fecha de ingreso son requeridos'}), 400
        
        alumno_existente = Alumno.get_by_id(alumno_id)
        if not alumno_existente:
            return jsonify({'error': 'Alumno no encontrado'}), 404
        
        Alumno.update(alumno_id, data['nombre'], data['correo'], data['fecha_ingreso'])
        return jsonify({'mensaje': 'Alumno actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alumno_bp.route('/alumnos/<int:alumno_id>', methods=['DELETE'])
def delete_alumno(alumno_id):
    """Elimina un alumno específico"""
    try:
        alumno_existente = Alumno.get_by_id(alumno_id)
        if not alumno_existente:
            return jsonify({'error': 'Alumno no encontrado'}), 404
        
        Alumno.delete(alumno_id)
        return jsonify({'mensaje': 'Alumno eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
