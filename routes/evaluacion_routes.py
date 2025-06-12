# filepath: routes/evaluacion_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from models.evaluacion import Evaluacion
from models.seccion import Seccion
from db.database import execute_query

evaluacion_bp = Blueprint('evaluacion', __name__)

def _verificar_seccion_cerrada(seccion_id):
    """Verifica si la sección pertenece a un curso cerrado"""
    query = """
    SELECT ic.cerrado
    FROM secciones s
    JOIN instancias_curso ic ON s.instancia_id = ic.id
    WHERE s.id = ?
    """
    resultado = execute_query(query, (seccion_id,))
    if resultado:
        return bool(resultado[0][0])
    return False

def _verificar_instancia_curso_cerrada(instancia_id):
    """Verifica si una instancia de curso está cerrada"""
    query = "SELECT cerrado FROM instancias_curso WHERE id = ?"
    resultado = execute_query(query, (instancia_id,))
    if resultado:
        return bool(resultado[0][0])
    return False

@evaluacion_bp.route('/evaluaciones')
def listar_evaluaciones():
    """Lista todas las evaluaciones"""
    evaluaciones = Evaluacion.obtener_todos()
    return render_template('evaluaciones/listar.html', evaluaciones=evaluaciones)

@evaluacion_bp.route('/evaluaciones/crear', methods=['GET', 'POST'])
def crear_evaluacion():
    """Crea una nueva evaluación"""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre'].strip()
            porcentaje = float(request.form['porcentaje'])
            seccion_id = int(request.form['seccion_id'])
            
            # Verificar que la sección no pertenezca a un curso cerrado
            if _verificar_seccion_cerrada(seccion_id):
                flash('No se pueden crear evaluaciones en un curso que ya ha sido cerrado', 'error')
                return redirect(url_for('evaluacion.crear_evaluacion'))
            
            # Validaciones básicas
            if not nombre:
                flash('El nombre de la evaluación es requerido', 'error')
                return redirect(url_for('evaluacion.crear_evaluacion'))
            
            if porcentaje <= 0 or porcentaje > 100:
                flash('El porcentaje debe estar entre 0 y 100', 'error')
                return redirect(url_for('evaluacion.crear_evaluacion'))
            
            Evaluacion.crear(nombre, porcentaje, seccion_id)
            flash('Evaluación creada exitosamente', 'success')
            return redirect(url_for('evaluacion.listar_evaluaciones'))
            
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al crear la evaluación: {str(e)}', 'error')
    
    # Filtrar secciones que pertenezcan solo a cursos abiertos
    todas_secciones = Seccion.obtener_todos()
    secciones = []
    for seccion in todas_secciones:
        if not _verificar_instancia_curso_cerrada(seccion['instancia_id']):
            secciones.append(seccion)
    
    return render_template('evaluaciones/crear.html', secciones=secciones)

@evaluacion_bp.route('/evaluaciones/<int:id>/editar', methods=['GET', 'POST'])
def editar_evaluacion(id):
    """Edita una evaluación"""
    evaluacion = Evaluacion.obtener_por_id(id)
    if not evaluacion:
        flash('Evaluación no encontrada', 'error')
        return redirect(url_for('evaluacion.listar_evaluaciones'))
    
    # Verificar si la sección actual pertenece a un curso cerrado
    if _verificar_seccion_cerrada(evaluacion.seccion_id):
        flash('No se pueden editar evaluaciones de un curso que ya ha sido cerrado', 'error')
        return redirect(url_for('evaluacion.listar_evaluaciones'))
    
    if request.method == 'POST':
        try:
            evaluacion.nombre = request.form['nombre'].strip()
            evaluacion.porcentaje = float(request.form['porcentaje'])
            nueva_seccion_id = int(request.form['seccion_id'])
            
            # Verificar que la nueva sección no pertenezca a un curso cerrado
            if _verificar_seccion_cerrada(nueva_seccion_id):
                flash('No se puede mover la evaluación a un curso que ya ha sido cerrado', 'error')
                return redirect(url_for('evaluacion.editar_evaluacion', id=id))
            
            evaluacion.seccion_id = nueva_seccion_id
            
            # Validaciones básicas
            if not evaluacion.nombre:
                flash('El nombre de la evaluación es requerido', 'error')
                return redirect(url_for('evaluacion.editar_evaluacion', id=id))
            
            if evaluacion.porcentaje <= 0 or evaluacion.porcentaje > 100:
                flash('El porcentaje debe estar entre 0 y 100', 'error')
                return redirect(url_for('evaluacion.editar_evaluacion', id=id))
            
            evaluacion.actualizar()
            flash('Evaluación actualizada exitosamente', 'success')
            return redirect(url_for('evaluacion.listar_evaluaciones'))
            
        except ValueError:
            flash('Error en los datos ingresados', 'error')
        except Exception as e:
            flash(f'Error al actualizar la evaluación: {str(e)}', 'error')
    
    # Filtrar secciones que pertenezcan solo a cursos abiertos
    todas_secciones = Seccion.obtener_todos()
    secciones = []
    for seccion in todas_secciones:
        if not _verificar_instancia_curso_cerrada(seccion['instancia_id']):
            secciones.append(seccion)
    
    return render_template('evaluaciones/editar.html', evaluacion=evaluacion, secciones=secciones)

@evaluacion_bp.route('/evaluaciones/<int:id>/eliminar', methods=['POST'])
def eliminar_evaluacion(id):
    """Elimina una evaluación"""
    try:
        # Obtener la evaluación antes de eliminarla para verificar si está cerrada
        evaluacion = Evaluacion.obtener_por_id(id)
        if not evaluacion:
            flash('Evaluación no encontrada', 'error')
            return redirect(url_for('evaluacion.listar_evaluaciones'))
        
        # Verificar si la sección pertenece a un curso cerrado
        if _verificar_seccion_cerrada(evaluacion.seccion_id):
            flash('No se pueden eliminar evaluaciones de un curso que ya ha sido cerrado', 'error')
            return redirect(url_for('evaluacion.listar_evaluaciones'))
        
        Evaluacion.eliminar(id)
        flash('Evaluación eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la evaluación: {str(e)}', 'error')
    
    return redirect(url_for('evaluacion.listar_evaluaciones'))
