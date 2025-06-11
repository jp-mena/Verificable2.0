from flask import Blueprint, request, jsonify
from models.curso import Curso

curso_bp = Blueprint('curso', __name__)

@curso_bp.route('/cursos', methods=['GET'])
def get_cursos():
    """Obtiene todos los cursos"""
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@curso_bp.route('/cursos', methods=['POST'])
def create_curso():
    """Crea un nuevo curso"""
    try:
        data = request.get_json()
        if not data or 'codigo' not in data or 'nombre' not in data:
            return jsonify({'error': 'Código y nombre son requeridos'}), 400
        
        curso = Curso(data['codigo'], data['nombre'], data.get('requisitos'))
        curso_id = curso.save()
        return jsonify({'id': curso_id, 'mensaje': 'Curso creado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@curso_bp.route('/cursos/<int:curso_id>', methods=['GET'])
def get_curso(curso_id):
    """Obtiene un curso específico"""
    try:
        curso = Curso.get_by_id(curso_id)
        if not curso:
            return jsonify({'error': 'Curso no encontrado'}), 404
        
        return jsonify({
            'id': curso[0],
            'codigo': curso[1],
            'nombre': curso[2],
            'requisitos': curso[3]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@curso_bp.route('/cursos/<int:curso_id>', methods=['PUT'])
def update_curso(curso_id):
    """Actualiza un curso específico"""
    try:
        data = request.get_json()
        if not data or 'codigo' not in data or 'nombre' not in data:
            return jsonify({'error': 'Código y nombre son requeridos'}), 400
        
        curso_existente = Curso.get_by_id(curso_id)
        if not curso_existente:
            return jsonify({'error': 'Curso no encontrado'}), 404
        
        Curso.update(curso_id, data['codigo'], data['nombre'], data.get('requisitos'))
        return jsonify({'mensaje': 'Curso actualizado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@curso_bp.route('/cursos/<int:curso_id>', methods=['DELETE'])
def delete_curso(curso_id):
    """Elimina un curso específico"""
    try:
        curso_existente = Curso.get_by_id(curso_id)
        if not curso_existente:
            return jsonify({'error': 'Curso no encontrado'}), 404
        
        Curso.delete(curso_id)
        return jsonify({'mensaje': 'Curso eliminado exitosamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
