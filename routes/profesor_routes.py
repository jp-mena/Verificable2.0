from flask import Blueprint, request, jsonify
from models.profesor import Profesor

profesor_bp = Blueprint('profesor', __name__)

@profesor_bp.route('/profesores', methods=['GET'])
def get_profesores():
    """Obtiene todos los profesores"""
    try:
        profesores = Profesor.get_all()
        profesores_list = []
        for profesor in profesores:
            profesores_list.append({
                'id': profesor[0],
                'nombre': profesor[1],
                'correo': profesor[2]
            })
        return jsonify({'profesores': profesores_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profesor_bp.route('/profesores', methods=['POST'])
def create_profesor():
    """Crea un nuevo profesor"""
    try:
        data = request.get_json()
        if not data or 'nombre' not in data or 'correo' not in data:
            return jsonify({'error': 'Nombre y correo son requeridos'}), 400
        
        profesor = Profesor(data['nombre'], data['correo'])
        profesor_id = profesor.save()
        return jsonify({'id': profesor_id, 'mensaje': 'Profesor creado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profesor_bp.route('/profesores/<int:profesor_id>', methods=['GET'])
def get_profesor(profesor_id):
    """Obtiene un profesor específico"""
    try:
        profesor = Profesor.get_by_id(profesor_id)
        if not profesor:
            return jsonify({'error': 'Profesor no encontrado'}), 404
        
        return jsonify({
            'id': profesor[0],
            'nombre': profesor[1],
            'correo': profesor[2]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profesor_bp.route('/profesores/<int:profesor_id>', methods=['PUT'])
def update_profesor(profesor_id):
    """Actualiza un profesor específico"""
    try:
        data = request.get_json()
        if not data or 'nombre' not in data or 'correo' not in data:
            return jsonify({'error': 'Nombre y correo son requeridos'}), 400
        
        profesor_existente = Profesor.get_by_id(profesor_id)
        if not profesor_existente:
            return jsonify({'error': 'Profesor no encontrado'}), 404
        
        Profesor.update(profesor_id, data['nombre'], data['correo'])
        return jsonify({'mensaje': 'Profesor actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profesor_bp.route('/profesores/<int:profesor_id>', methods=['DELETE'])
def delete_profesor(profesor_id):
    """Elimina un profesor específico"""
    try:
        profesor_existente = Profesor.get_by_id(profesor_id)
        if not profesor_existente:
            return jsonify({'error': 'Profesor no encontrado'}), 404
        
        Profesor.delete(profesor_id)
        return jsonify({'mensaje': 'Profesor eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
